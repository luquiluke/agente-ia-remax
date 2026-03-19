"""
Calculadoras — ReMax Buenos Aires
──────────────────────────────────
4 calculadoras en tabs:
  1. Comision ReMax (tabla + co-broke)
  2. Gastos de escritura CABA 2026
  3. Rentabilidad inversor
  4. Analisis pozo / fideicomiso
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from config import settings
from market_data import (
    REMAX_TABLAS, get_barrios_list, get_barrios_by_zona,
    EXPENSAS_TIPICAS_ARS, get_benchmark,
)
from calculators import (
    calcular_comision,
    calcular_escritura,
    calcular_rentabilidad,
    calcular_pozo,
)

REMAX_RED = "#E31837"
REMAX_BLUE = "#003DA5"

st.set_page_config(
    page_title="Calculadoras — ReMax BA",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(f"""
<style>
  .calc-card {{
    background:#f8f9fa; border-left:4px solid {REMAX_BLUE};
    padding:16px 20px; border-radius:6px; margin:12px 0;
    font-size:14px; line-height:1.8;
  }}
  .result-highlight {{
    font-size:28px; font-weight:bold; color:{REMAX_RED};
  }}
  .result-label {{
    font-size:12px; color:#888; margin-bottom:2px;
  }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<h1 style='color:{REMAX_BLUE}; margin-bottom:4px'>Calculadoras ReMax</h1>
<p style='color:gray;margin-top:0'>
  Herramientas financieras para agentes en Buenos Aires &middot;
  <span style='color:{REMAX_RED}'>Todos los valores en USD</span>
</p>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Comision ReMax",
    "Gastos de Escritura CABA",
    "Rentabilidad Inversor",
    "Analisis Pozo",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Comisión ReMax
# ──────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Calculadora de Comision ReMax</h3>", unsafe_allow_html=True)
    st.caption("Calcula cuanto cobra el agente segun la tabla y si hay co-broke.")

    col_in, col_out = st.columns([1, 1])

    with col_in:
        precio_c1 = st.number_input(
            "Precio de venta (USD)",
            min_value=1_000, max_value=10_000_000,
            value=200_000, step=5_000, key="c1_precio",
        )
        comision_pct_c1 = st.slider(
            "Comision total (%)",
            min_value=2.0, max_value=6.0, value=4.0, step=0.5, key="c1_com",
        )
        tabla_nombre_c1 = st.selectbox(
            "Tu tabla",
            list(REMAX_TABLAS.keys()),
            index=list(REMAX_TABLAS.keys()).index("Tabla 60% (estándar)"),
            key="c1_tabla",
        )
        tabla_pct_c1 = REMAX_TABLAS[tabla_nombre_c1]
        cobroke_c1 = st.checkbox("Operacion co-broke (otro agente en la parte contraria)", key="c1_cobroke")

        split_label = "¿Como se divide la comision?"
        split_c1 = st.selectbox(
            split_label,
            ["50% comprador / 50% vendedor", "100% comprador", "100% vendedor"],
            key="c1_split",
        )
        split_map = {
            "50% comprador / 50% vendedor": 0.5,
            "100% comprador": 1.0,
            "100% vendedor": 0.0,
        }
        split_pct = split_map[split_c1]

    with col_out:
        res_c1 = calcular_comision(
            precio_venta_usd=precio_c1,
            comision_pct=comision_pct_c1 / 100,
            tabla_pct=tabla_pct_c1,
            cobroke=cobroke_c1,
            split_comprador_vendedor=split_pct,
        )

        st.markdown(f"<div class='result-label'>Comision bruta total</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-highlight'>USD {res_c1.comision_bruta_usd:,.0f}</div>", unsafe_allow_html=True)

        st.markdown("---")
        m1, m2 = st.columns(2)
        m1.metric("Tu neto (sin co-broke)", f"USD {res_c1.neto_agente_usd:,.0f}")
        m2.metric("Franquicia ReMax", f"USD {res_c1.franquicia_usd:,.0f}")
        if cobroke_c1:
            st.metric("Tu neto CON co-broke", f"USD {res_c1.parte_agente_cobroke_usd:,.0f}", delta=f"-USD {res_c1.neto_agente_usd - res_c1.parte_agente_cobroke_usd:,.0f}")

        st.markdown("---")
        m3, m4 = st.columns(2)
        m3.metric("Paga el comprador", f"USD {res_c1.comision_bruta_comprador_usd:,.0f}")
        m4.metric("Paga el vendedor", f"USD {res_c1.comision_bruta_vendedor_usd:,.0f}")

    # Resumen para copiar
    with st.expander("Copiar resumen"):
        st.code(res_c1.resumen(), language="")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Gastos de escritura CABA
# ──────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Gastos de Escritura CABA 2026</h3>", unsafe_allow_html=True)
    st.caption(
        "Estimacion basada en el Colegio de Escribanos CABA + AFIP + ARBA. "
        "Siempre confirmar con el escribano interviniente."
    )

    col_in2, col_out2 = st.columns([1, 1])

    with col_in2:
        precio_esc = st.number_input(
            "Precio de escritura (USD)",
            min_value=1_000, max_value=10_000_000,
            value=200_000, step=5_000, key="c2_precio",
        )
        pre2018 = st.radio(
            "La propiedad fue adquirida por el vendedor...",
            ["Antes del 01/01/2018 (aplica ITI 1.5%)", "Desde el 01/01/2018 en adelante (aplica Ganancias)"],
            key="c2_iti",
        )
        aplica_iti = "Antes" in pre2018

        st.info(
            "El **ITI** (Impuesto a la Transferencia de Inmuebles, 1.5% AFIP) aplica solo "
            "a propiedades adquiridas **antes** del 01/01/2018. Las posteriores quedan "
            "alcanzadas por el impuesto a las ganancias sobre la plusvalia (15% escalonado).",
            icon="ℹ️",
        )

    with col_out2:
        res_c2 = calcular_escritura(precio_escritura_usd=precio_esc, propiedad_pre_2018=aplica_iti)

        c_col, v_col = st.columns(2)
        with c_col:
            st.markdown(f"<b style='color:{REMAX_BLUE}'>COMPRADOR</b>", unsafe_allow_html=True)
            st.metric("Sello CABA (ITE 50%)", f"USD {res_c2.sello_comprador_usd:,.0f}")
            st.metric("Honorarios escribano", f"USD {res_c2.escribano_comprador_usd:,.0f}")
            st.metric("Registro RPI", f"USD {res_c2.rpi_usd:,.0f}")
            st.metric("Estudio juridico", f"USD {res_c2.estudio_juridico_usd:,.0f}")
            st.markdown(f"<div class='result-label'>Total comprador</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='result-highlight'>USD {res_c2.total_comprador_usd:,.0f}</div> "
                f"<span style='color:#888'>({res_c2.total_comprador_pct*100:.1f}%)</span>",
                unsafe_allow_html=True,
            )

        with v_col:
            st.markdown(f"<b style='color:{REMAX_RED}'>VENDEDOR</b>", unsafe_allow_html=True)
            st.metric("Sello CABA (ITE 50%)", f"USD {res_c2.sello_vendedor_usd:,.0f}")
            if aplica_iti:
                st.metric("ITI AFIP (1.5%)", f"USD {res_c2.iti_usd:,.0f}")
            else:
                st.metric("ITI AFIP", "No aplica", help="Post-2018 → Ganancias sobre plusvalia")
            st.metric("Honorarios escribano", f"USD {res_c2.escribano_vendedor_usd:,.0f}")
            st.markdown(f"<div class='result-label'>Total vendedor</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='result-highlight'>USD {res_c2.total_vendedor_usd:,.0f}</div> "
                f"<span style='color:#888'>({res_c2.total_vendedor_pct*100:.1f}%)</span>",
                unsafe_allow_html=True,
            )

    st.metric(
        "TOTAL GASTOS DE LA OPERACION",
        f"USD {res_c2.total_operacion_usd:,.0f}",
        help="Comprador + vendedor",
    )

    with st.expander("Copiar resumen"):
        st.code(res_c2.resumen(), language="")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — Rentabilidad inversor
# ──────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Rentabilidad para el Inversor</h3>", unsafe_allow_html=True)
    st.caption("Calcula la rentabilidad bruta y neta de una propiedad como inversion de alquiler.")

    col_in3, col_out3 = st.columns([1, 1])

    with col_in3:
        precio_r = st.number_input(
            "Precio de compra (USD)",
            min_value=1_000, max_value=10_000_000,
            value=150_000, step=5_000, key="c3_precio",
        )
        alquiler_r = st.number_input(
            "Alquiler mensual estimado (USD)",
            min_value=0, max_value=100_000,
            value=600, step=50, key="c3_alquiler",
            help="Ingresa el valor de alquiler en USD que esperan cobrar",
        )

        # Expensas
        tipo_expensas = st.selectbox(
            "Tipo de edificio (expensas)",
            list(EXPENSAS_TIPICAS_ARS.keys()),
            key="c3_exp_tipo",
        )
        exp_data = EXPENSAS_TIPICAS_ARS[tipo_expensas]
        expensas_sugeridas = exp_data["avg"]
        expensas_r = st.number_input(
            f"Expensas mensuales (ARS) — sugerido: {expensas_sugeridas:,.0f}",
            min_value=0, max_value=5_000_000,
            value=expensas_sugeridas, step=5_000, key="c3_exp",
        )

        tc_r = st.number_input(
            "Tipo de cambio blue (ARS/USD)",
            value=settings.tc_blue_int, step=50, key="c3_tc",
        )
        incluir_gastos = st.checkbox(
            "Incluir gastos de entrada (escritura + comision) en el payback",
            value=True, key="c3_gastos",
        )

    with col_out3:
        if alquiler_r > 0:
            res_c3 = calcular_rentabilidad(
                precio_compra_usd=precio_r,
                alquiler_mensual_usd=alquiler_r,
                expensas_mensuales_ars=expensas_r,
                tc_blue=tc_r,
                incluir_gastos_entrada=incluir_gastos,
            )

            # Semaforo de clasificacion
            clas_color = {
                "Excelente": "#27ae60",
                "Buena": "#2ecc71",
                "Regular": "#f39c12",
                "Baja": "#e74c3c",
            }
            clas_base = res_c3.clasificacion.split(" ")[0]
            color_clas = clas_color.get(clas_base, "#888")

            st.markdown(
                f"<div style='background:{color_clas};color:white;padding:12px 16px;"
                f"border-radius:8px;font-size:18px;font-weight:bold;text-align:center'>"
                f"{res_c3.clasificacion}</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            r1, r2 = st.columns(2)
            r1.metric("Rentabilidad bruta", f"{res_c3.rentabilidad_bruta_pct:.1f}%")
            r2.metric("Rentabilidad neta", f"{res_c3.rentabilidad_neta_pct:.1f}%")

            r3, r4 = st.columns(2)
            r3.metric("Ingreso neto mensual", f"USD {res_c3.ingreso_neto_mensual_usd:,.0f}")
            r4.metric("Ingreso neto anual", f"USD {res_c3.ingreso_neto_anual_usd:,.0f}")

            r5, r6 = st.columns(2)
            r5.metric("Expensas (en USD)", f"USD {res_c3.expensas_mensuales_usd:,.0f}/mes")
            r6.metric("Payback estimado", f"{res_c3.payback_anos:.1f} años")

            if incluir_gastos:
                st.metric("Gastos de entrada est.", f"USD {res_c3.gastos_entrada_usd:,.0f}")

        else:
            st.info("Ingresa el alquiler mensual para calcular la rentabilidad.")

    with st.expander("Copiar resumen"):
        if alquiler_r > 0:
            st.code(res_c3.resumen(), language="")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — Análisis pozo
# ──────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown(f"<h3 style='color:{REMAX_BLUE}'>Analisis de Inversion en Pozo</h3>", unsafe_allow_html=True)
    st.caption(
        "Calcula la plusvalia esperada y el ROI de comprar una unidad en fideicomiso al costo "
        "(en pozo) vs. el precio de mercado al momento de la entrega."
    )

    col_in4, col_out4 = st.columns([1, 1])
    all_barrios = get_barrios_list()

    with col_in4:
        precio_pozo = st.number_input(
            "Precio en pozo (USD)",
            min_value=1_000, max_value=10_000_000,
            value=135_000, step=5_000, key="c4_precio",
        )
        superficie_pozo = st.number_input(
            "Superficie (m²)",
            min_value=10.0, max_value=1000.0,
            value=54.0, step=1.0, key="c4_sup",
        )
        barrio_pozo = st.selectbox(
            "Barrio",
            all_barrios,
            index=all_barrios.index("Palermo") if "Palermo" in all_barrios else 0,
            key="c4_barrio",
        )

        bench_pozo = get_benchmark(barrio_pozo)
        if bench_pozo:
            st.info(
                f"Benchmark {barrio_pozo}: "
                f"USD {bench_pozo['min']:,}–{bench_pozo['max']:,}/m² "
                f"(promedio USD {bench_pozo['avg']:,}/m²)",
                icon="📊",
            )

        meses_entrega = st.slider(
            "Meses hasta la entrega",
            min_value=3, max_value=60, value=24, step=3, key="c4_meses",
        )
        adelanto_p = st.slider(
            "Adelanto (%)",
            min_value=10, max_value=60, value=30, step=5, key="c4_adelanto",
        )

        # Precio m² de mercado (manual o automático)
        usar_benchmark = st.checkbox(
            f"Usar benchmark de {barrio_pozo} (USD {bench_pozo['avg']:,}/m²)" if bench_pozo else "Usar benchmark",
            value=True, key="c4_bench",
        )
        precio_m2_manual = None
        if not usar_benchmark:
            precio_m2_manual = st.number_input(
                "Precio/m² de mercado al entregar (USD)",
                min_value=500, max_value=20_000,
                value=bench_pozo["avg"] if bench_pozo else 3000,
                step=100, key="c4_m2",
            )

    with col_out4:
        res_c4 = calcular_pozo(
            precio_pozo_usd=precio_pozo,
            superficie_m2=superficie_pozo,
            barrio=barrio_pozo,
            meses_hasta_entrega=meses_entrega,
            adelanto_pct=adelanto_p / 100,
            precio_m2_mercado=precio_m2_manual,
        )

        # Clasificacion
        clas_colors_p = {
            "Excelente": "#27ae60",
            "Buena": "#2ecc71",
            "Regular": "#f39c12",
            "Baja": "#e74c3c",
        }
        clas_base_p = res_c4.clasificacion.split(" ")[0]
        color_clas_p = clas_colors_p.get(clas_base_p, "#888")
        st.markdown(
            f"<div style='background:{color_clas_p};color:white;padding:12px 16px;"
            f"border-radius:8px;font-size:18px;font-weight:bold;text-align:center'>"
            f"{res_c4.clasificacion}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        p1, p2 = st.columns(2)
        p1.metric("Precio/m² en pozo", f"USD {res_c4.precio_m2_pozo_usd:,.0f}")
        p2.metric("Precio/m² mercado", f"USD {res_c4.precio_m2_mercado_usd:,.0f}")

        p3, p4 = st.columns(2)
        p3.metric("Plusvalia esperada", f"{res_c4.plusvalia_esperada_pct:.1f}%")
        p4.metric("ROI estimado", f"{res_c4.roi_pct:.1f}%")

        p5, p6 = st.columns(2)
        p5.metric("Valor al entregar (est.)", f"USD {res_c4.valor_estimado_entrega_usd:,.0f}")
        p6.metric("Ganancia neta est.", f"USD {res_c4.ganancia_neta_usd:,.0f}")

        st.divider()
        st.markdown("**Plan de pagos estimado**")
        pp1, pp2, pp3 = st.columns(3)
        pp1.metric("Adelanto", f"USD {res_c4.adelanto_usd:,.0f}")
        pp2.metric("Cuota mensual", f"USD {res_c4.cuota_mensual_usd:,.0f}")
        pp3.metric("Meses hasta entrega", f"{res_c4.meses_hasta_entrega}")

        st.caption(
            f"Gastos escritura al vender: USD {res_c4.gastos_escritura_usd:,.0f} (est. incluidos en la ganancia neta)"
        )

    with st.expander("Copiar resumen"):
        st.code(res_c4.resumen(), language="")
