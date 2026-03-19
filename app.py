"""
app.py — Home del Agente IA de ReMax Buenos Aires
──────────────────────────────────────────────────
Pagina de inicio con branding ReMax (rojo #E31837, azul #003DA5)
sin logo. Acceso a las 3 herramientas principales.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from config import settings
from market_data import get_barrios_by_zona

REMAX_RED = "#E31837"
REMAX_BLUE = "#003DA5"

st.set_page_config(
    page_title="Agente IA ReMax Buenos Aires",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Global ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* Navbar / sidebar accent */
  [data-testid="stSidebar"] {{
    border-right: 3px solid {REMAX_RED};
  }}

  /* Botones primarios */
  .stButton>button[kind="primary"] {{
    background-color: {REMAX_RED} !important;
    border: none !important;
  }}
  .stButton>button[kind="primary"]:hover {{
    background-color: #c0122c !important;
  }}

  /* Cards de herramientas */
  .tool-card {{
    background: #fff;
    border: 1px solid #e0e0e0;
    border-top: 4px solid {REMAX_RED};
    border-radius: 8px;
    padding: 20px 24px;
    margin: 8px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    height: 100%;
  }}
  .tool-card h3 {{
    color: {REMAX_BLUE};
    margin-top: 0;
    font-size: 18px;
  }}
  .tool-card p {{
    color: #555;
    font-size: 14px;
    line-height: 1.6;
  }}
  .tool-card .badge {{
    display: inline-block;
    background: {REMAX_BLUE};
    color: white;
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    margin-right: 4px;
    margin-bottom: 4px;
  }}

  /* Hero */
  .hero {{
    background: linear-gradient(135deg, {REMAX_BLUE} 0%, #002a7a 100%);
    color: white;
    padding: 40px 48px;
    border-radius: 12px;
    margin-bottom: 24px;
  }}
  .hero h1 {{
    font-size: 32px;
    margin-bottom: 8px;
    font-weight: 800;
  }}
  .hero span.red {{ color: {REMAX_RED}; }}
  .hero p {{
    opacity: 0.85;
    font-size: 16px;
    margin: 0;
  }}

  /* Stats bar */
  .stats-bar {{
    display: flex;
    gap: 24px;
    margin-top: 24px;
    flex-wrap: wrap;
  }}
  .stat-item {{
    background: rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 10px 20px;
    text-align: center;
  }}
  .stat-item .val {{
    font-size: 22px;
    font-weight: bold;
    color: white;
  }}
  .stat-item .lbl {{
    font-size: 11px;
    opacity: 0.7;
    display: block;
  }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:16px 0'>
      <div style='font-size:36px'>🏢</div>
      <div style='font-size:20px;font-weight:bold;color:{REMAX_BLUE}'>ReMax</div>
      <div style='font-size:12px;color:{REMAX_RED};font-weight:bold'>BUENOS AIRES</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("### Herramientas")
    st.page_link("pages/1_Scanner.py", label="Scanner de oportunidades", icon="🔍")
    st.page_link("pages/2_Calculadoras.py", label="Calculadoras", icon="🧮")
    st.page_link("pages/3_Asistente.py", label="Asistente IA", icon="🤖")

    st.divider()
    st.markdown("### Estado del sistema")
    st.markdown(f"{'✅' if settings.OPENAI_API_KEY else '❌'} OpenAI (GPT-4o-mini)")
    st.markdown(f"{'✅' if settings.remax_scraper_configurado else '⚠️'} Scraper ReMax {'(live)' if settings.remax_scraper_configurado else '(demo)'}")
    st.markdown(f"{'✅' if settings.google_configurado else '⚠️'} Google Sheets {'(live)' if settings.google_configurado else '(demo)'}")
    st.markdown(f"{'✅' if settings.gmail_configurado else '⚠️'} Gmail {'(live)' if settings.gmail_configurado else '(demo)'}")

    st.divider()
    st.caption("Agente IA ReMax BA v1.0 · 2026")

# ── Hero ───────────────────────────────────────────────────────────────────────
# Cobertura de barrios
barrios_por_zona = get_barrios_by_zona()
total_barrios = sum(len(v) for v in barrios_por_zona.values())

st.markdown(f"""
<div class='hero'>
  <h1>Agente IA <span class='red'>ReMax</span> Buenos Aires</h1>
  <p>
    Scanner diario de propiedades &middot; Calculadoras especializadas &middot;
    Analisis de inversion con IA
  </p>
  <div class='stats-bar'>
    <div class='stat-item'>
      <div class='val'>{total_barrios}</div>
      <div class='lbl'>Barrios con benchmarks</div>
    </div>
    <div class='stat-item'>
      <div class='val'>4</div>
      <div class='lbl'>Calculadoras</div>
    </div>
    <div class='stat-item'>
      <div class='val'>GPT-4o</div>
      <div class='lbl'>Motor de IA</div>
    </div>
    <div class='stat-item'>
      <div class='val'>USD</div>
      <div class='lbl'>Moneda operaciones</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Cards de herramientas ──────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
<div class='tool-card'>
  <h3>🔍 Scanner de Oportunidades</h3>
  <p>
    Escanea propiedades en ReMax Buenos Aires, calcula metricas de inversion
    para cada una y genera un reporte IA con las mejores oportunidades del dia.
  </p>
  <div>
    <span class='badge'>Precio/m² vs. barrio</span>
    <span class='badge'>Rentabilidad</span>
    <span class='badge'>DOM</span>
    <span class='badge'>Grade A-F</span>
    <span class='badge'>Reporte GPT</span>
    <span class='badge'>Email diario</span>
  </div>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/1_Scanner.py", label="Abrir Scanner", use_container_width=True)

with col2:
    st.markdown(f"""
<div class='tool-card'>
  <h3>🧮 Calculadoras</h3>
  <p>
    4 calculadoras especializadas para el mercado de Buenos Aires:
    comision ReMax con tabla y co-broke, gastos de escritura CABA 2026,
    rentabilidad del inversor y analisis de pozo/fideicomiso.
  </p>
  <div>
    <span class='badge'>Tabla ReMax 45-80%</span>
    <span class='badge'>Co-broke</span>
    <span class='badge'>Escritura CABA</span>
    <span class='badge'>ITI / Ganancias</span>
    <span class='badge'>ROI</span>
    <span class='badge'>Pozo</span>
  </div>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/2_Calculadoras.py", label="Abrir Calculadoras", use_container_width=True)

with col3:
    st.markdown(f"""
<div class='tool-card'>
  <h3>🤖 Asistente IA</h3>
  <p>
    Chat con conocimiento del mercado porteño. Compara barrios, analiza precios,
    sugiere estrategias de negociacion y responde dudas sobre comisiones,
    escrituras e inversiones.
  </p>
  <div>
    <span class='badge'>Benchmarks CABA/GBA</span>
    <span class='badge'>Estrategia</span>
    <span class='badge'>Negociacion</span>
    <span class='badge'>Espanol rioplatense</span>
  </div>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/3_Asistente.py", label="Abrir Asistente", use_container_width=True)

# ── Benchmarks rápidos ─────────────────────────────────────────────────────────
st.divider()
st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Benchmarks de Mercado (USD/m² — 2026)</h3>", unsafe_allow_html=True)

import pandas as pd
from market_data import BENCHMARK_M2

bench_df_data = []
for barrio, data in BENCHMARK_M2.items():
    bench_df_data.append({
        "Barrio": barrio,
        "Zona": data["zona"],
        "Min USD/m²": data["min"],
        "Max USD/m²": data["max"],
        "Prom USD/m²": data["avg"],
        "Renta bruta %": data["rentabilidad_pct"],
    })

bench_df = pd.DataFrame(bench_df_data)

zona_filter = st.selectbox(
    "Filtrar por zona",
    ["Todas"] + sorted(bench_df["Zona"].unique().tolist()),
    key="home_zona",
)

if zona_filter != "Todas":
    bench_df = bench_df[bench_df["Zona"] == zona_filter]

st.dataframe(
    bench_df.sort_values("Prom USD/m²", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Min USD/m²": st.column_config.NumberColumn(format="USD %d"),
        "Max USD/m²": st.column_config.NumberColumn(format="USD %d"),
        "Prom USD/m²": st.column_config.NumberColumn(format="USD %d"),
        "Renta bruta %": st.column_config.NumberColumn(format="%.1f%%"),
    },
)

# ── Quick start ────────────────────────────────────────────────────────────────
st.divider()
st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Inicio rapido</h3>", unsafe_allow_html=True)

with st.expander("Como configurar la app"):
    st.markdown("""
1. **Copiá `.env.example` a `.env`** y completá tu `OPENAI_API_KEY`
2. **Scanner en vivo:** completá `REMAX_EMAIL` y `REMAX_PASSWORD` (credenciales ReMax)
3. **Google Sheets:** creá un proyecto en Google Cloud, descargá las credenciales del service account
   y copiá el ID del spreadsheet
4. **Email diario:** configurá `GMAIL_ADDRESS` + `GMAIL_APP_PASSWORD` (App Password de Gmail)
5. **Ejecutar la app:**
   ```bash
   streamlit run app.py
   ```
   O con Docker:
   ```bash
   docker build -t agente-remax . && docker run -p 8501:8501 agente-remax
   ```
""")

with st.expander("Cobertura de barrios"):
    for zona, barrios in sorted(barrios_por_zona.items()):
        st.markdown(f"**{zona}** ({len(barrios)} barrios): {', '.join(barrios)}")
