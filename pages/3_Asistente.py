"""
Asistente IA — ReMax Buenos Aires (v2 placeholder)
────────────────────────────────────────────────────
Chat con conocimiento del mercado porteño.
En MVP: responde preguntas sobre barrios, métricas y calculadoras.
En v2: integración completa con LangGraph + herramientas.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from openai import OpenAI

from config import settings
from market_data import get_benchmark, get_barrios_by_zona, BENCHMARK_M2

REMAX_RED = "#E31837"
REMAX_BLUE = "#003DA5"

st.set_page_config(
    page_title="Asistente IA — ReMax BA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h3 style='color:{REMAX_RED}'>Asistente ReMax</h3>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### Preguntas de ejemplo")
    ejemplos = {
        "Comparar barrios": "¿Cuál es mejor para invertir: Palermo o Caballito?",
        "Precio m² Belgrano": "¿Cuánto vale el m² en Belgrano? ¿Está caro o barato el mercado?",
        "Rentabilidad San Telmo": "Si compro en San Telmo a USD 2.100/m², ¿cuánto sería la rentabilidad bruta?",
        "DOM como herramienta": "¿Cómo uso los días en mercado para negociar con el vendedor?",
        "Calcular comisión": "Tengo una venta de USD 280.000 con tabla 65%, ¿cuánto me llevo?",
        "Pozo vs usado": "¿Cuándo conviene más un pozo que un usado?",
    }

    for label, prompt in ejemplos.items():
        if st.button(label, use_container_width=True, key=f"ej_{label}"):
            st.session_state["asist_prefill"] = prompt
            st.rerun()

    st.divider()
    st.markdown(f"{'✅' if settings.OPENAI_API_KEY else '❌'} OpenAI")

    if st.button("Limpiar conversacion", use_container_width=True):
        st.session_state.pop("asist_msgs", None)
        st.rerun()

    st.divider()
    st.caption(
        "**v2 — próximamente:** búsqueda de propiedades en tiempo real, "
        "reserva de visitas en Google Calendar, "
        "redacción de emails para clientes."
    )

# ── System prompt con contexto del mercado ────────────────────────────────────
def _build_system_prompt() -> str:
    barrios_info = []
    for barrio, data in list(BENCHMARK_M2.items())[:20]:  # top 20 para no saturar el context
        barrios_info.append(
            f"- {barrio} ({data['zona']}): USD {data['min']:,}–{data['max']:,}/m² "
            f"(avg USD {data['avg']:,}/m², renta bruta {data['rentabilidad_pct']}%)"
        )

    return f"""Sos un asistente inmobiliario experto de ReMax Argentina, especializado en Buenos Aires (CABA y GBA).

Tu rol: ayudar a agentes de ReMax con análisis de mercado, cálculos de inversión, estrategias de negociación y conocimiento del mercado porteño.

DATOS DEL MERCADO (USD/m², promedio dpto. usado 2026):
{chr(10).join(barrios_info)}

REGLAS:
- Siempre respondés en español rioplatense (tuteás, usás "vos")
- Todos los valores en USD (así opera el mercado de BA)
- Sos directo, práctico y usás datos concretos
- Si te preguntan algo que no sabés con certeza, lo decís claramente
- Cuando calculás comisiones, usás el modelo ReMax: agente cobra 45-80% del bruto
- La comisión total típica en BA es 3-6% del precio de venta
- Gastos escritura CABA: comprador ~2.7%, vendedor ~1.3-2.8% (con/sin ITI)
- DOM (días en mercado): <15 días = mercado caliente; >60 días = margen de negociación
- El mercado de BA opera SOLO en USD para operaciones de compraventa

Podés ayudar con:
1. Comparar barrios y zonas
2. Analizar si un precio está alto/bajo vs. el benchmark
3. Calcular rentabilidades de alquiler
4. Explicar el sistema de tablas de ReMax
5. Estrategias de negociación
6. Análisis de operaciones en pozo
7. Gastos de escritura y costos de la operación
"""

# ── Session state ──────────────────────────────────────────────────────────────
if "asist_msgs" not in st.session_state:
    st.session_state.asist_msgs = []

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='color:{REMAX_BLUE}; margin-bottom:4px'>Asistente IA ReMax</h1>
<p style='color:gray; margin-top:0'>
  Tu consultor de mercado inmobiliario porteño &middot;
  <span style='color:{REMAX_RED}'>Powered by GPT-4o-mini</span>
</p>
""", unsafe_allow_html=True)

# Mensaje de bienvenida
if not st.session_state.asist_msgs:
    with st.chat_message("assistant", avatar="🏡"):
        st.markdown(
            "¡Hola! Soy el Asistente IA de **ReMax Buenos Aires**. "
            "Puedo ayudarte con:\n\n"
            "- Comparar barrios y analizar precios/m²\n"
            "- Calcular rentabilidades y comisiones\n"
            "- Estrategias de negociación con el DOM\n"
            "- Análisis de operaciones en pozo\n"
            "- Costos de escritura CABA 2026\n\n"
            "¿Qué querés saber?"
        )

# Historial
for msg in st.session_state.asist_msgs:
    avatar = "🏡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Input ──────────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("asist_prefill", None)
user_input = st.chat_input("Preguntame sobre barrios, precios, comisiones, inversiones...")
if prefill and not user_input:
    user_input = prefill

if user_input:
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.asist_msgs.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="🏡"):
        if not settings.OPENAI_API_KEY:
            resp = "⚠️ Falta la OPENAI_API_KEY. Configurala en el archivo .env para usar el asistente."
            st.markdown(resp)
        else:
            with st.spinner("Pensando..."):
                try:
                    client = OpenAI(api_key=settings.OPENAI_API_KEY)

                    messages = [{"role": "system", "content": _build_system_prompt()}]
                    for m in st.session_state.asist_msgs:
                        messages.append({"role": m["role"], "content": m["content"]})

                    response = client.chat.completions.create(
                        model=settings.OPENAI_MODEL,
                        messages=messages,
                        temperature=0.4,
                        max_tokens=800,
                    )
                    resp = response.choices[0].message.content or "No pude generar una respuesta."
                except Exception as e:
                    resp = f"Error al llamar a OpenAI: {str(e)}"

            st.markdown(resp)

    st.session_state.asist_msgs.append({"role": "assistant", "content": resp})
