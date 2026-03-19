"""
report_generator.py — Generador de reportes IA y envío por email
─────────────────────────────────────────────────────────────────
Genera un reporte diario en español rioplatense usando GPT y lo
envía por Gmail SMTP (HTML) o lo muestra en el dashboard.
"""
from __future__ import annotations

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from config import settings
from investment_analyzer import MetricasInversion, resumen_portfolio

# ─── Generación del reporte con GPT ──────────────────────────────────────────

def generar_reporte(
    metricas_list: list[MetricasInversion],
    barrios_buscados: list[str] | None = None,
    modo_scraping: str = "demo",
) -> str:
    """
    Genera un reporte de inversión inmobiliaria en español rioplatense usando GPT.
    Retorna el texto del reporte (markdown).
    """
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    resumen = resumen_portfolio(metricas_list)
    top_3 = metricas_list[:3]
    fecha = datetime.now().strftime("%d/%m/%Y")

    # Construir el prompt
    top_3_texto = ""
    for i, m in enumerate(top_3, 1):
        p = m.propiedad
        top_3_texto += (
            f"\n{i}. {p.titulo} — {p.barrio} ({p.zona})\n"
            f"   Precio: USD {p.precio_usd:,.0f} | {p.superficie_m2:.0f} m² | "
            f"USD {m.precio_m2_usd:,.0f}/m²\n"
            f"   Benchmark barrio: USD {m.precio_m2_barrio_avg:,.0f}/m² → {m.precio_m2_etiqueta}\n"
            f"   Rentabilidad bruta estimada: {m.rentabilidad_bruta_pct:.1f}%\n"
            f"   DOM: {p.dias_en_mercado} días → {m.dom_etiqueta}\n"
            f"   Comisión neta agente: USD {m.neto_agente_usd:,.0f}\n"
            f"   Grade: {m.grade} (score {m.score:.0f}/100)\n"
            f"   Highlights: {', '.join(m.highlights) if m.highlights else 'Sin highlights'}\n"
            f"   Alertas: {', '.join(m.alertas) if m.alertas else 'Ninguna'}\n"
        )

    todas_texto = ""
    for m in metricas_list[:10]:
        p = m.propiedad
        todas_texto += (
            f"  • {p.barrio}: USD {p.precio_usd:,.0f} | {p.superficie_m2:.0f}m² | "
            f"{m.precio_m2_etiqueta} | Renta {m.rentabilidad_bruta_pct:.1f}% | Grade {m.grade}\n"
        )

    prompt = f"""Sos un analista inmobiliario senior de ReMax Argentina especializado en
inversiones en Buenos Aires. Tu tarea es redactar el reporte diario de oportunidades
para un agente ReMax.

Fecha: {fecha}
Fuente de datos: {'ReMax.com.ar (vivo)' if 'live' in modo_scraping else 'Datos demo (modo prueba)'}
Barrios analizados: {', '.join(barrios_buscados) if barrios_buscados else 'Toda CABA y GBA'}
Total propiedades analizadas: {resumen.get('total_propiedades', 0)}

ESTADÍSTICAS GENERALES:
- Precio promedio: USD {resumen.get('precio_promedio_usd', 0):,.0f}
- Precio/m² promedio: USD {resumen.get('m2_promedio_usd', 0):,.0f}
- Rentabilidad promedio: {resumen.get('rentabilidad_promedio_pct', 0):.1f}%
- Distribución de grades: {resumen.get('grades', {})}
- Comisión total estimada del portfolio: USD {resumen.get('comision_total_estimada_usd', 0):,.0f}

TOP 3 OPORTUNIDADES DE HOY:
{top_3_texto}

RESUMEN DE PROPIEDADES ANALIZADAS:
{todas_texto}

---
Redactá un reporte profesional en español rioplatense (tuteo, voceo argentino) con estas secciones:
1. **Resumen ejecutivo** (2-3 oraciones sobre el mercado del día)
2. **Top 3 oportunidades** (descripción detallada, por qué llaman la atención, qué argumento usar con el cliente)
3. **Señales de mercado** (tendencias de precio, DOM, zonas con movimiento)
4. **Recomendación de acción** (qué hacer hoy: qué propiedades priorizar, cómo encarar la negociación)
5. **Advertencias** (propiedades sobrevaluadas o con riesgos)

El tono debe ser profesional pero cercano, como un colega experimentado que le habla a otro agente.
Usá datos concretos (USD, %) siempre que puedas.
Máximo 600 palabras."""

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos un analista inmobiliario de ReMax Argentina. "
                        "Siempre respondés en español argentino, con datos precisos y recomendaciones accionables."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1000,
        )
        return response.choices[0].message.content or "No se pudo generar el reporte."
    except Exception as e:
        return f"Error al generar reporte con IA: {str(e)}\n\nVerificá la OPENAI_API_KEY en el .env."


# ─── Generación de WhatsApp text ──────────────────────────────────────────────

def generar_texto_whatsapp(metricas_list: list[MetricasInversion]) -> str:
    """
    Genera un texto listo para copiar y pegar en WhatsApp.
    Sin formato markdown — emojis simples.
    """
    fecha = datetime.now().strftime("%d/%m/%Y")
    top = metricas_list[:3]

    lineas = [
        f"*REMAX — Oportunidades del dia {fecha}*",
        "",
    ]

    for i, m in enumerate(top, 1):
        p = m.propiedad
        lineas += [
            f"*{i}. {p.titulo}*",
            f"Barrio: {p.barrio} | USD {p.precio_usd:,.0f}",
            f"Precio/m2: USD {m.precio_m2_usd:,.0f} ({m.precio_m2_etiqueta})",
            f"Renta estimada: {m.rentabilidad_bruta_pct:.1f}% bruta",
            f"Grade: {m.grade}",
            "",
        ]

    lineas.append("_Generado por Agente IA ReMax_")
    return "\n".join(lineas)


# ─── Envío de email ───────────────────────────────────────────────────────────

def _construir_html(
    reporte_md: str,
    metricas_list: list[MetricasInversion],
    fecha: str,
) -> str:
    """Convierte el reporte markdown a HTML con estilos ReMax."""

    # Conversión markdown básica a HTML
    html_body = reporte_md
    html_body = html_body.replace("\n\n", "</p><p>")
    html_body = html_body.replace("\n", "<br>")

    # Bold (**texto**)
    import re
    html_body = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html_body)
    # Italic (*texto*)
    html_body = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html_body)
    # Headers (## Título)
    html_body = re.sub(r"#{1,3} (.+?)(<br>|</p>)", r"<h3>\1</h3>", html_body)

    top_rows = ""
    for m in metricas_list[:5]:
        p = m.propiedad
        grade_color = m.grade_color
        precio_color = m.precio_m2_color
        top_rows += f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee">{p.barrio}</td>
          <td style="padding:8px;border-bottom:1px solid #eee">{p.tipo}</td>
          <td style="padding:8px;border-bottom:1px solid #eee">USD {p.precio_usd:,.0f}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;color:{precio_color}">
            USD {m.precio_m2_usd:,.0f}/m²
          </td>
          <td style="padding:8px;border-bottom:1px solid #eee">{m.rentabilidad_bruta_pct:.1f}%</td>
          <td style="padding:8px;border-bottom:1px solid #eee;
              background:{grade_color};color:white;text-align:center;
              border-radius:4px;font-weight:bold">{m.grade}</td>
        </tr>"""

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; color: #333; max-width: 700px; margin: 0 auto; }}
    .header {{ background: #003DA5; color: white; padding: 20px; }}
    .header h1 {{ margin: 0; font-size: 22px; }}
    .header p {{ margin: 4px 0 0; opacity: 0.8; font-size: 13px; }}
    .remax-red {{ color: #E31837; }}
    .body {{ padding: 24px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; }}
    th {{ background: #E31837; color: white; padding: 10px 8px; text-align: left; }}
    .footer {{ background: #f5f5f5; padding: 16px; font-size: 12px; color: #888; text-align: center; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>ReMax <span style="color:#E31837">&#9632;</span> Reporte Diario de Oportunidades</h1>
    <p>{fecha} &nbsp;|&nbsp; Agente IA Buenos Aires</p>
  </div>
  <div class="body">
    <p>{html_body}</p>
    <h3 style="color:#003DA5">Top 5 Propiedades del Dia</h3>
    <table>
      <tr>
        <th>Barrio</th><th>Tipo</th><th>Precio</th><th>USD/m2</th><th>Renta</th><th>Grade</th>
      </tr>
      {top_rows}
    </table>
  </div>
  <div class="footer">
    Generado por Agente IA ReMax Argentina &nbsp;&middot;&nbsp;
    <span class="remax-red">remax.com.ar</span>
  </div>
</body>
</html>"""


def enviar_reporte_email(
    reporte_md: str,
    metricas_list: list[MetricasInversion],
    destinatario: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Envía el reporte por email via Gmail SMTP.
    Retorna (exito, mensaje).
    """
    if not settings.gmail_configurado:
        return False, "Gmail no configurado. Completá GMAIL_ADDRESS y GMAIL_APP_PASSWORD en el .env."

    destinatario = destinatario or settings.REPORT_RECIPIENT_EMAIL
    if not destinatario:
        return False, "No hay destinatario configurado (REPORT_RECIPIENT_EMAIL en .env)."

    fecha = datetime.now().strftime("%d/%m/%Y")
    asunto = f"ReMax — Oportunidades del dia {fecha}"
    html = _construir_html(reporte_md, metricas_list, fecha)

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.GMAIL_ADDRESS
        msg["To"] = destinatario
        msg["Subject"] = asunto

        # Texto plano como fallback
        texto_plano = reporte_md
        msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.GMAIL_ADDRESS, settings.GMAIL_APP_PASSWORD)
            server.sendmail(settings.GMAIL_ADDRESS, destinatario, msg.as_string())

        return True, f"Reporte enviado a {destinatario}"
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"
