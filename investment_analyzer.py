"""
investment_analyzer.py — Análisis de inversión para propiedades ReMax Buenos Aires
──────────────────────────────────────────────────────────────────────────────────
Calcula métricas clave para cada propiedad del scanner:
  - Precio/m² vs. benchmark del barrio
  - Rentabilidad bruta anual % (con expensas)
  - DOM como señal de negociación
  - Potencial de revalorización
  - Comisión estimada ReMax
  - Grade de inversión (A/B/C/D)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from market_data import clasificar_precio_m2, get_benchmark, BENCHMARK_M2
from remax_scraper import PropiedadRemax
from calculators import calcular_comision, calcular_rentabilidad
from config import settings


# ─── Modelo de métricas ───────────────────────────────────────────────────────

@dataclass
class MetricasInversion:
    propiedad: PropiedadRemax

    # Precio m²
    precio_m2_usd: float = 0.0
    precio_m2_barrio_avg: float = 0.0
    precio_m2_etiqueta: str = ""
    precio_m2_color: str = "#888888"
    diff_benchmark_pct: float = 0.0

    # Rentabilidad
    alquiler_estimado_mensual_usd: float = 0.0
    rentabilidad_bruta_pct: float = 0.0
    rentabilidad_neta_pct: float = 0.0      # descontando expensas

    # DOM
    dom_etiqueta: str = ""
    dom_color: str = "#888888"
    margen_negociacion_pct: float = 0.0

    # Comisión ReMax
    comision_bruta_usd: float = 0.0
    neto_agente_usd: float = 0.0

    # Revalorización
    potencial_revalorizacion_pct: float = 0.0

    # Grade final
    grade: str = "C"
    grade_color: str = "#f39c12"
    score: float = 0.0
    highlights: list[str] = field(default_factory=list)
    alertas: list[str] = field(default_factory=list)


# ─── Parámetros de análisis ───────────────────────────────────────────────────

@dataclass
class ParametrosAnalisis:
    comision_total_pct: float = 0.04    # % total comisión sobre precio
    tabla_pct: float = 0.60             # tabla del agente
    cobroke: bool = False
    tc_blue: int = 1_250                # ARS/USD
    # Alquiler como % del valor de la propiedad (mensual, por tipo de zona)
    yield_mensual_por_zona: dict = field(default_factory=lambda: {
        "CABA": 0.004,        # 0.4%/mes = 4.8% bruto anual (conservador CABA)
        "GBA Norte": 0.0038,
        "GBA Oeste": 0.005,
        "GBA Sur": 0.005,
    })


# ─── Clasificadores auxiliares ────────────────────────────────────────────────

def _clasificar_dom(dias: int) -> tuple[str, str, float]:
    """
    Clasifica los días en mercado y estima el margen de negociación.
    Retorna (etiqueta, color_css, margen_negociacion_pct).
    """
    if dias == 0:
        return "Recién publicada", "#27ae60", 0.0
    elif dias <= 14:
        return f"Reciente ({dias}d)", "#27ae60", 1.0
    elif dias <= 30:
        return f"Normal ({dias}d)", "#f39c12", 3.0
    elif dias <= 60:
        return f"Tiempo en mercado ({dias}d)", "#e67e22", 5.0
    elif dias <= 90:
        return f"Demora notable ({dias}d)", "#e74c3c", 8.0
    else:
        return f"Larga estadía ({dias}d)", "#c0392b", 12.0


def _calcular_revalorizacion(barrio: str, tipo_prop: str, antiguedad: int) -> float:
    """
    Estima el potencial de revalorización anual % basado en zona y características.
    """
    bench = get_benchmark(barrio)
    if bench is None:
        return 3.0

    zona = bench.get("zona", "CABA")

    # Base por zona
    base = {
        "CABA": 4.0,
        "GBA Norte": 3.5,
        "GBA Oeste": 3.0,
        "GBA Sur": 3.0,
    }.get(zona, 3.5)

    # Ajuste por tipo
    if tipo_prop in ("PH", "Casa"):
        base += 0.5

    # Ajuste por antigüedad (a estrenar = más plusvalía, muy viejo = menos)
    if antiguedad == 0:
        base += 1.0        # pozo / a estrenar
    elif antiguedad <= 5:
        base += 0.5
    elif antiguedad >= 30:
        base -= 0.5

    return round(base, 1)


def _calcular_grade(score: float) -> tuple[str, str]:
    """Convierte score 0-100 en grade y color."""
    if score >= 80:
        return "A", "#27ae60"
    elif score >= 65:
        return "B", "#2ecc71"
    elif score >= 50:
        return "C", "#f39c12"
    elif score >= 35:
        return "D", "#e67e22"
    else:
        return "F", "#e74c3c"


# ─── Función principal ────────────────────────────────────────────────────────

def analizar_propiedad(
    propiedad: PropiedadRemax,
    params: Optional[ParametrosAnalisis] = None,
) -> MetricasInversion:
    """
    Analiza una propiedad y retorna sus métricas de inversión.
    """
    if params is None:
        params = ParametrosAnalisis(
            comision_total_pct=settings.comision_bruta_float,
            tabla_pct=settings.remax_tabla_float,
            tc_blue=settings.tc_blue_int,
        )

    metricas = MetricasInversion(propiedad=propiedad)

    # ── Precio m² ────────────────────────────────────────────────────────────
    metricas.precio_m2_usd = propiedad.precio_m2_usd
    bench = get_benchmark(propiedad.barrio)
    if bench:
        metricas.precio_m2_barrio_avg = bench["avg"]
        metricas.diff_benchmark_pct = round(
            ((metricas.precio_m2_usd - bench["avg"]) / bench["avg"]) * 100, 1
        ) if bench["avg"] > 0 else 0
    etiqueta, color = clasificar_precio_m2(metricas.precio_m2_usd, propiedad.barrio)
    metricas.precio_m2_etiqueta = etiqueta
    metricas.precio_m2_color = color

    # ── Alquiler estimado ─────────────────────────────────────────────────────
    yield_m = params.yield_mensual_por_zona.get(propiedad.zona, 0.004)
    metricas.alquiler_estimado_mensual_usd = round(propiedad.precio_usd * yield_m, 0)

    # ── Rentabilidad ──────────────────────────────────────────────────────────
    if propiedad.operacion == "Venta" and metricas.alquiler_estimado_mensual_usd > 0:
        rent = calcular_rentabilidad(
            precio_compra_usd=propiedad.precio_usd,
            alquiler_mensual_usd=metricas.alquiler_estimado_mensual_usd,
            expensas_mensuales_ars=propiedad.expensas_ars,
            tc_blue=params.tc_blue,
            incluir_gastos_entrada=False,
        )
        metricas.rentabilidad_bruta_pct = rent.rentabilidad_bruta_pct
        metricas.rentabilidad_neta_pct = rent.rentabilidad_neta_pct
    elif bench:
        # Usar benchmark del barrio si no hay alquiler calculado
        metricas.rentabilidad_bruta_pct = bench.get("rentabilidad_pct", 5.0)
        metricas.rentabilidad_neta_pct = round(metricas.rentabilidad_bruta_pct * 0.85, 2)

    # ── DOM ───────────────────────────────────────────────────────────────────
    dom_label, dom_color, margen = _clasificar_dom(propiedad.dias_en_mercado)
    metricas.dom_etiqueta = dom_label
    metricas.dom_color = dom_color
    metricas.margen_negociacion_pct = margen

    # ── Comisión ReMax ────────────────────────────────────────────────────────
    if propiedad.precio_usd > 0:
        com = calcular_comision(
            precio_venta_usd=propiedad.precio_usd,
            comision_pct=params.comision_total_pct,
            tabla_pct=params.tabla_pct,
            cobroke=params.cobroke,
        )
        metricas.comision_bruta_usd = com.comision_bruta_usd
        metricas.neto_agente_usd = com.neto_agente_usd

    # ── Revalorización ────────────────────────────────────────────────────────
    metricas.potencial_revalorizacion_pct = _calcular_revalorizacion(
        propiedad.barrio, propiedad.tipo, propiedad.antiguedad_anos
    )

    # ── Score y grade ─────────────────────────────────────────────────────────
    score = 50.0  # base

    # +/- por precio vs. benchmark (max ±20 pts)
    diff = metricas.diff_benchmark_pct
    if diff <= -15:
        score += 20
        metricas.highlights.append("Precio muy por debajo del barrio (ganga potencial)")
    elif diff <= -5:
        score += 10
        metricas.highlights.append(f"Precio bajo de barrio ({diff:+.0f}%)")
    elif diff > 15:
        score -= 20
        metricas.alertas.append(f"Precio sobrevaluado vs. barrio ({diff:+.0f}%)")
    elif diff > 5:
        score -= 10

    # +/- por rentabilidad (max ±20 pts)
    rent = metricas.rentabilidad_bruta_pct
    if rent >= 6.5:
        score += 20
        metricas.highlights.append(f"Alta rentabilidad estimada ({rent:.1f}%)")
    elif rent >= 5.0:
        score += 10
        metricas.highlights.append(f"Buena rentabilidad ({rent:.1f}%)")
    elif rent < 3.5:
        score -= 15
        metricas.alertas.append(f"Rentabilidad baja ({rent:.1f}%)")

    # +/- por DOM como señal de negociación
    if propiedad.dias_en_mercado > 60:
        score += 10
        metricas.highlights.append(f"Larga estadía en mercado → mayor margen negociación (~{margen:.0f}%)")
    elif propiedad.dias_en_mercado <= 5:
        score -= 5

    # +/- por antigüedad y estado
    if propiedad.antiguedad_anos == 0:
        score += 5
        metricas.highlights.append("A estrenar / en pozo")
    elif propiedad.antiguedad_anos > 40:
        score -= 5

    # +/- por potencial revalorización
    if metricas.potencial_revalorizacion_pct >= 5:
        score += 10
        metricas.highlights.append(f"Zona con alto potencial de revalorización ({metricas.potencial_revalorizacion_pct:.1f}%/año)")

    metricas.score = round(min(100, max(0, score)), 1)
    metricas.grade, metricas.grade_color = _calcular_grade(metricas.score)

    return metricas


def analizar_portfolio(
    propiedades: list[PropiedadRemax],
    params: Optional[ParametrosAnalisis] = None,
) -> list[MetricasInversion]:
    """
    Analiza una lista de propiedades y retorna métricas ordenadas por score.
    """
    metricas_list = [analizar_propiedad(p, params) for p in propiedades]
    return sorted(metricas_list, key=lambda m: m.score, reverse=True)


def resumen_portfolio(metricas_list: list[MetricasInversion]) -> dict:
    """
    Estadísticas generales del portfolio analizado.
    """
    if not metricas_list:
        return {}

    precios = [m.propiedad.precio_usd for m in metricas_list]
    m2s = [m.precio_m2_usd for m in metricas_list if m.precio_m2_usd > 0]
    rents = [m.rentabilidad_bruta_pct for m in metricas_list if m.rentabilidad_bruta_pct > 0]
    comisiones = [m.neto_agente_usd for m in metricas_list if m.neto_agente_usd > 0]

    grades_count = {}
    for m in metricas_list:
        grades_count[m.grade] = grades_count.get(m.grade, 0) + 1

    return {
        "total_propiedades": len(metricas_list),
        "precio_promedio_usd": round(sum(precios) / len(precios), 0) if precios else 0,
        "precio_min_usd": min(precios) if precios else 0,
        "precio_max_usd": max(precios) if precios else 0,
        "m2_promedio_usd": round(sum(m2s) / len(m2s), 0) if m2s else 0,
        "rentabilidad_promedio_pct": round(sum(rents) / len(rents), 1) if rents else 0,
        "comision_total_estimada_usd": round(sum(comisiones), 0),
        "comision_promedio_usd": round(sum(comisiones) / len(comisiones), 0) if comisiones else 0,
        "grades": grades_count,
        "top_barrios": _top_barrios(metricas_list),
        "gangas": [m for m in metricas_list if "Ganga" in m.precio_m2_etiqueta],
        "alto_dom": [m for m in metricas_list if m.propiedad.dias_en_mercado > 60],
    }


def _top_barrios(metricas_list: list[MetricasInversion], top_n: int = 5) -> list[dict]:
    """Barrios con mayor score promedio."""
    barrios: dict[str, list[float]] = {}
    for m in metricas_list:
        barrios.setdefault(m.propiedad.barrio, []).append(m.score)
    ranking = [
        {"barrio": b, "score_promedio": round(sum(s) / len(s), 1), "n": len(s)}
        for b, s in barrios.items()
    ]
    return sorted(ranking, key=lambda x: x["score_promedio"], reverse=True)[:top_n]
