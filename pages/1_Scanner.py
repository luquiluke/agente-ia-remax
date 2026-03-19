"""
Scanner de Oportunidades — ReMax Buenos Aires
─────────────────────────────────────────────
Flujo completo:
  1. Buscar propiedades (ReMax scraper o mock)
  2. Analizar cada propiedad (métricas inversión)
  3. Guardar en Google Sheets (opcional)
  4. Generar reporte IA (GPT-4o-mini)
  5. Enviar por email / copiar para WhatsApp
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import datetime

from config import settings
from market_data import get_barrios_list, get_barrios_by_zona, REMAX_TABLAS
from remax_scraper import buscar_propiedades, PropiedadRemax
from investment_analyzer import (
    analizar_portfolio,
    resumen_portfolio,
    ParametrosAnalisis,
    MetricasInversion,
)

# ── Colores ReMax ──────────────────────────────────────────────────────────────
REMAX_RED = "#E31837"
REMAX_BLUE = "#003DA5"

st.set_page_config(
    page_title="Scanner — ReMax BA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ReMax ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    .grade-badge {{
        display:inline-block; padding:2px 10px; border-radius:12px;
        color:white; font-weight:bold; font-size:14px;
    }}
    .highlight-card {{
        background:#f8f9fa; border-left:4px solid {REMAX_RED};
        padding:12px 16px; border-radius:4px; margin:8px 0;
    }}
    .metric-label {{ color:#666; font-size:12px; margin-bottom:2px; }}
    .metric-value {{ font-size:20px; font-weight:bold; color:{REMAX_BLUE}; }}
    .stProgress > div > div > div {{ background-color: {REMAX_RED}; }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h3 style='color:{REMAX_RED}'>Parametros del Scanner</h3>", unsafe_allow_html=True)
    st.divider()

    # Barrios
    barrios_por_zona = get_barrios_by_zona()
    todos_barrios = get_barrios_list()

    filtrar_barrios = st.checkbox("Filtrar por barrios", value=False)
    barrios_sel = []
    if filtrar_barrios:
        zona_sel = st.selectbox("Zona", list(barrios_por_zona.keys()))
        barrios_zona = barrios_por_zona.get(zona_sel, [])
        barrios_sel = st.multiselect(
            "Barrios",
            barrios_zona,
            default=barrios_zona[:3] if barrios_zona else [],
        )

    st.divider()

    # Precios
    st.markdown("**Rango de precio (USD)**")
    col1, col2 = st.columns(2)
    with col1:
        precio_min = st.number_input("Min", value=50_000, step=10_000, format="%d")
    with col2:
        precio_max = st.number_input("Max", value=500_000, step=10_000, format="%d")

    # Operación
    operacion = st.selectbox("Operacion", ["Todos", "Venta", "Alquiler", "Pozo"])

    st.divider()

    # Parámetros ReMax
    st.markdown("**Configuracion ReMax**")
    tabla_nombre = st.selectbox(
        "Tu tabla",
        list(REMAX_TABLAS.keys()),
        index=list(REMAX_TABLAS.keys()).index("Tabla 60% (estándar)"),
    )
    tabla_pct = REMAX_TABLAS[tabla_nombre]
    st.caption(f"Tabla seleccionada: {tabla_pct*100:.0f}%")

    comision_pct = st.slider(
        "Comision total (%)",
        min_value=2.0, max_value=6.0, value=4.0, step=0.5,
    ) / 100

    cobroke = st.checkbox("Incluir co-broke (50/50)", value=False)

    st.divider()

    # Tipo de cambio
    tc_blue = st.number_input("TC Blue (ARS/USD)", value=settings.tc_blue_int, step=50)

    st.divider()

    max_props = st.number_input("Max propiedades", value=20, min_value=5, max_value=100)

    # Status
    st.divider()
    st.markdown("**Estado de integraciones**")
    st.markdown(f"{'✅' if settings.OPENAI_API_KEY else '❌'} OpenAI")
    st.markdown(f"{'✅' if settings.remax_scraper_configurado else '⚠️'} ReMax scraper {'(live)' if settings.remax_scraper_configurado else '(demo)'}")
    st.markdown(f"{'✅' if settings.google_configurado else '⚠️'} Google Sheets {'(live)' if settings.google_configurado else '(demo)'}")
    st.markdown(f"{'✅' if settings.gmail_configurado else '⚠️'} Gmail {'(live)' if settings.gmail_configurado else '(demo)'}")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='color:{REMAX_BLUE}; margin-bottom:4px'>
    Scanner de Oportunidades
</h1>
<p style='color:gray; margin-top:0'>
    Analisis diario de propiedades en Buenos Aires &middot;
    <span style='color:{REMAX_RED}'>ReMax Argentina</span>
</p>
""", unsafe_allow_html=True)

st.divider()

# ── Botón principal ────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 3])
with col_btn:
    run_scan = st.button(
        "Escanear propiedades",
        type="primary",
        use_container_width=True,
    )
with col_info:
    if not settings.remax_scraper_configurado:
        st.info(
            "Modo demo activo. Configurá REMAX_EMAIL y REMAX_PASSWORD en .env "
            "para scrapear ReMax.com.ar en tiempo real.",
            icon="ℹ️",
        )

# ── Resultado del scan ─────────────────────────────────────────────────────────
if run_scan or "remax_metricas" in st.session_state:

    if run_scan:
        params = ParametrosAnalisis(
            comision_total_pct=comision_pct,
            tabla_pct=tabla_pct,
            cobroke=cobroke,
            tc_blue=tc_blue,
        )

        with st.spinner("Buscando propiedades..."):
            propiedades, modo = buscar_propiedades(
                barrios=barrios_sel if filtrar_barrios and barrios_sel else None,
                precio_min=precio_min,
                precio_max=precio_max,
                operacion=operacion.lower() if operacion != "Todos" else "todos",
                max_resultados=max_props,
            )

        if not propiedades:
            st.warning("No se encontraron propiedades con los filtros indicados.")
            st.stop()

        with st.spinner(f"Analizando {len(propiedades)} propiedades..."):
            metricas_list = analizar_portfolio(propiedades, params)

        st.session_state["remax_metricas"] = metricas_list
        st.session_state["remax_modo"] = modo
        st.session_state["remax_params"] = params
        st.session_state["remax_barrios"] = barrios_sel if filtrar_barrios else []

        modo_label = {
            "live_auth": "ReMax.com.ar (autenticado)",
            "live_publico": "ReMax.com.ar (publico)",
            "demo": "Datos demo",
        }.get(modo, modo)

        st.success(f"{len(propiedades)} propiedades encontradas y analizadas — Fuente: {modo_label}")

    # Recuperar del state
    metricas_list: list[MetricasInversion] = st.session_state["remax_metricas"]
    modo = st.session_state.get("remax_modo", "demo")
    params = st.session_state.get("remax_params", ParametrosAnalisis())

    resumen = resumen_portfolio(metricas_list)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Resumen del Mercado</h3>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Propiedades", resumen["total_propiedades"])
    k2.metric("Precio promedio", f"USD {resumen['precio_promedio_usd']:,.0f}")
    k3.metric("Precio/m² prom.", f"USD {resumen['m2_promedio_usd']:,.0f}")
    k4.metric("Renta prom.", f"{resumen['rentabilidad_promedio_pct']:.1f}%")
    k5.metric("Comision total est.", f"USD {resumen['comision_total_estimada_usd']:,.0f}")

    # Grades
    grades = resumen.get("grades", {})
    grade_cols = st.columns(len(grades) if grades else 1)
    for col, (g, n) in zip(grade_cols, sorted(grades.items())):
        colors = {"A": REMAX_BLUE, "B": "#27ae60", "C": "#f39c12", "D": "#e67e22", "F": "#e74c3c"}
        grade_color = colors.get(g, "#888")
        col.markdown(
            f"<div style='text-align:center'>"
            f"<div style='font-size:28px;font-weight:bold;color:{grade_color}'>{n}</div>"
            f"<div style='font-size:12px;color:#666'>Grade {g}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Top 3 ─────────────────────────────────────────────────────────────────
    st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Top 3 Oportunidades del Dia</h3>", unsafe_allow_html=True)
    top_3 = metricas_list[:3]
    tcols = st.columns(3)

    for col, m in zip(tcols, top_3):
        p = m.propiedad
        with col:
            st.markdown(f"""
<div class='highlight-card'>
  <div style='font-weight:bold;color:{REMAX_BLUE};font-size:14px'>{p.titulo}</div>
  <div style='color:#888;font-size:12px'>{p.barrio} · {p.tipo} · {p.operacion}</div>
  <div style='margin:8px 0'>
    <span style='font-size:20px;font-weight:bold'>USD {p.precio_usd:,.0f}</span>
    <span style='font-size:12px;color:#888'> / {p.superficie_m2:.0f} m²</span>
  </div>
  <div style='font-size:12px'>
    USD {m.precio_m2_usd:,.0f}/m²
    <span style='color:{m.precio_m2_color}'>
      {m.precio_m2_etiqueta}
    </span>
  </div>
  <div style='font-size:12px'>Renta bruta: <b>{m.rentabilidad_bruta_pct:.1f}%</b></div>
  <div style='font-size:12px'>DOM: <span style='color:{m.dom_color}'>{m.dom_etiqueta}</span></div>
  <div style='font-size:12px'>Comision neta: <b>USD {m.neto_agente_usd:,.0f}</b></div>
  <div style='margin-top:8px'>
    <span class='grade-badge' style='background:{m.grade_color}'>Grade {m.grade}</span>
    <span style='font-size:11px;color:#888'> Score {m.score:.0f}/100</span>
  </div>
</div>
""", unsafe_allow_html=True)
            if m.highlights:
                for h in m.highlights[:2]:
                    st.markdown(f"✅ {h}")
            if m.alertas:
                for a in m.alertas[:1]:
                    st.markdown(f"⚠️ {a}")

    st.divider()

    # ── Tabla completa ────────────────────────────────────────────────────────
    st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Todas las Propiedades</h3>", unsafe_allow_html=True)

    tabla_data = []
    for m in metricas_list:
        p = m.propiedad
        tabla_data.append({
            "ID": p.id,
            "Barrio": p.barrio,
            "Tipo": p.tipo,
            "Op.": p.operacion,
            "Precio USD": f"{p.precio_usd:,.0f}",
            "Sup. m²": f"{p.superficie_m2:.0f}",
            "USD/m²": f"{m.precio_m2_usd:,.0f}",
            "vs. Barrio": m.precio_m2_etiqueta.split("(")[0].strip(),
            "Renta %": f"{m.rentabilidad_bruta_pct:.1f}%",
            "DOM": p.dias_en_mercado,
            "Comision neta": f"USD {m.neto_agente_usd:,.0f}",
            "Grade": m.grade,
            "Score": m.score,
        })

    df = pd.DataFrame(tabla_data)

    def color_grade(val):
        colors = {"A": REMAX_BLUE, "B": "#27ae60", "C": "#f39c12", "D": "#e67e22", "F": "#e74c3c"}
        bg = colors.get(val, "#fff")
        return f"background-color:{bg};color:white;font-weight:bold;text-align:center"

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score", min_value=0, max_value=100, format="%.0f"
            ),
        },
    )

    # Descarga CSV
    csv_data = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "Descargar CSV",
        data=csv_data,
        file_name=f"remax_scan_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

    st.divider()

    # ── Google Sheets ─────────────────────────────────────────────────────────
    with st.expander("Guardar en Google Sheets", expanded=False):
        if settings.google_configurado:
            if st.button("Guardar en Sheets"):
                try:
                    import gspread
                    from google.oauth2.service_account import Credentials

                    scopes = [
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive",
                    ]
                    creds = Credentials.from_service_account_file(
                        settings.GOOGLE_SHEETS_CREDENTIALS, scopes=scopes
                    )
                    gc = gspread.authorize(creds)
                    sh = gc.open_by_key(settings.GOOGLE_SPREADSHEET_ID)

                    try:
                        ws = sh.worksheet(settings.PROPIEDADES_SHEET)
                        ws.clear()
                    except gspread.WorksheetNotFound:
                        ws = sh.add_worksheet(settings.PROPIEDADES_SHEET, 1000, 20)

                    rows = [list(df.columns)] + df.values.tolist()
                    ws.update("A1", rows)
                    st.success(f"Guardado en Sheets: {len(metricas_list)} propiedades")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Configurá Google Sheets en el .env para activar esta función.")

    # ── Reporte IA ────────────────────────────────────────────────────────────
    st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Reporte IA del Dia</h3>", unsafe_allow_html=True)

    col_gen, col_email = st.columns([1, 1])

    with col_gen:
        gen_reporte = st.button("Generar reporte con IA", type="primary", use_container_width=True)

    with col_email:
        email_dest = st.text_input(
            "Email destino",
            value=settings.REPORT_RECIPIENT_EMAIL,
            placeholder="tu@email.com",
        )

    if gen_reporte:
        if not settings.OPENAI_API_KEY:
            st.error("Falta la OPENAI_API_KEY en el .env.")
        else:
            with st.spinner("Generando reporte con GPT..."):
                from report_generator import generar_reporte, generar_texto_whatsapp, enviar_reporte_email

                barrios_buscados = st.session_state.get("remax_barrios", [])
                reporte = generar_reporte(metricas_list, barrios_buscados, modo)

            st.session_state["remax_reporte"] = reporte

    if "remax_reporte" in st.session_state:
        reporte = st.session_state["remax_reporte"]

        with st.expander("Ver reporte completo", expanded=True):
            st.markdown(reporte)

        # WhatsApp
        from report_generator import generar_texto_whatsapp, enviar_reporte_email

        wa_text = generar_texto_whatsapp(metricas_list)
        st.text_area("Copiar para WhatsApp", value=wa_text, height=200)

        # Email
        if st.button("Enviar reporte por email", use_container_width=True):
            if not email_dest:
                st.error("Ingresa un email destino.")
            elif not settings.gmail_configurado:
                st.warning("Gmail no configurado. Completá GMAIL_ADDRESS y GMAIL_APP_PASSWORD en el .env.")
            else:
                with st.spinner("Enviando email..."):
                    ok, msg = enviar_reporte_email(reporte, metricas_list, email_dest)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
