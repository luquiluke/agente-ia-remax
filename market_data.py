"""
market_data.py — Datos de mercado inmobiliario de Buenos Aires
──────────────────────────────────────────────────────────────
Benchmarks de precio USD/m² por barrio para CABA y GBA.
Fuentes: Reporte Inmobiliario, ZonaProp, Properati (2025-2026).

Actualizar manualmente cada trimestre o usar scraping de ZonaProp.
"""
from __future__ import annotations

# ── Benchmarks USD/m² por barrio (promedio departamento usado, 2026) ──────────
# Formato: "Barrio": {"min": X, "max": Y, "avg": Z, "zona": "CABA"|"GBA"}
BENCHMARK_M2: dict[str, dict] = {
    # ── CABA — Zona Norte Premium ──────────────────────────────────────────
    "Puerto Madero":        {"min": 4200, "max": 6500, "avg": 5200, "zona": "CABA", "rentabilidad_pct": 3.5},
    "Recoleta":             {"min": 2800, "max": 4000, "avg": 3300, "zona": "CABA", "rentabilidad_pct": 4.5},
    "Palermo":              {"min": 2500, "max": 3500, "avg": 2900, "zona": "CABA", "rentabilidad_pct": 5.2},
    "Belgrano":             {"min": 2200, "max": 3200, "avg": 2650, "zona": "CABA", "rentabilidad_pct": 4.8},
    "Núñez":                {"min": 2000, "max": 2900, "avg": 2400, "zona": "CABA", "rentabilidad_pct": 5.0},
    "Colegiales":           {"min": 2000, "max": 2800, "avg": 2350, "zona": "CABA", "rentabilidad_pct": 5.3},
    "Saavedra":             {"min": 1700, "max": 2400, "avg": 2050, "zona": "CABA", "rentabilidad_pct": 5.1},

    # ── CABA — Zona Centro / Corredor Norte ────────────────────────────────
    "Villa Crespo":         {"min": 1900, "max": 2600, "avg": 2200, "zona": "CABA", "rentabilidad_pct": 5.5},
    "Chacarita":            {"min": 1700, "max": 2400, "avg": 2050, "zona": "CABA", "rentabilidad_pct": 5.6},
    "Caballito":            {"min": 1700, "max": 2400, "avg": 2000, "zona": "CABA", "rentabilidad_pct": 5.3},
    "Almagro":              {"min": 1600, "max": 2200, "avg": 1850, "zona": "CABA", "rentabilidad_pct": 5.7},
    "Palermo Chico":        {"min": 3200, "max": 4500, "avg": 3800, "zona": "CABA", "rentabilidad_pct": 4.0},
    "Las Cañitas":          {"min": 2400, "max": 3200, "avg": 2750, "zona": "CABA", "rentabilidad_pct": 5.0},
    "Soho / Palermo Hollywood": {"min": 2600, "max": 3400, "avg": 2950, "zona": "CABA", "rentabilidad_pct": 5.4},
    "Barrio Norte":         {"min": 2500, "max": 3500, "avg": 2950, "zona": "CABA", "rentabilidad_pct": 4.6},

    # ── CABA — Zona Sur / Este ─────────────────────────────────────────────
    "San Telmo":            {"min": 1800, "max": 2600, "avg": 2100, "zona": "CABA", "rentabilidad_pct": 5.8},
    "Montserrat":           {"min": 1500, "max": 2200, "avg": 1800, "zona": "CABA", "rentabilidad_pct": 5.5},
    "La Boca":              {"min": 1000, "max": 1600, "avg": 1250, "zona": "CABA", "rentabilidad_pct": 6.5},
    "Barracas":             {"min": 1100, "max": 1700, "avg": 1350, "zona": "CABA", "rentabilidad_pct": 6.2},
    "Parque Patricios":     {"min": 1200, "max": 1800, "avg": 1450, "zona": "CABA", "rentabilidad_pct": 6.0},
    "Constitución":         {"min": 1100, "max": 1700, "avg": 1350, "zona": "CABA", "rentabilidad_pct": 6.3},
    "Boedo":                {"min": 1500, "max": 2000, "avg": 1700, "zona": "CABA", "rentabilidad_pct": 5.8},

    # ── CABA — Zona Oeste ──────────────────────────────────────────────────
    "Flores":               {"min": 1200, "max": 1800, "avg": 1500, "zona": "CABA", "rentabilidad_pct": 6.0},
    "Floresta":             {"min": 1100, "max": 1600, "avg": 1300, "zona": "CABA", "rentabilidad_pct": 6.2},
    "Villa del Parque":     {"min": 1400, "max": 2000, "avg": 1650, "zona": "CABA", "rentabilidad_pct": 5.9},
    "Villa Devoto":         {"min": 1400, "max": 2000, "avg": 1680, "zona": "CABA", "rentabilidad_pct": 5.8},
    "Villa Urquiza":        {"min": 1600, "max": 2300, "avg": 1900, "zona": "CABA", "rentabilidad_pct": 5.6},
    "Agronomía":            {"min": 1300, "max": 1800, "avg": 1500, "zona": "CABA", "rentabilidad_pct": 6.0},
    "Monte Castro":         {"min": 1100, "max": 1600, "avg": 1300, "zona": "CABA", "rentabilidad_pct": 6.3},
    "Mataderos":            {"min": 800,  "max": 1300, "avg": 1050, "zona": "CABA", "rentabilidad_pct": 6.8},
    "Liniers":              {"min": 900,  "max": 1400, "avg": 1100, "zona": "CABA", "rentabilidad_pct": 6.7},
    "Villa Luro":           {"min": 1000, "max": 1500, "avg": 1200, "zona": "CABA", "rentabilidad_pct": 6.5},
    "Lugano":               {"min": 700,  "max": 1100, "avg": 900,  "zona": "CABA", "rentabilidad_pct": 7.2},
    "Versalles":            {"min": 1200, "max": 1700, "avg": 1430, "zona": "CABA", "rentabilidad_pct": 6.1},

    # ── GBA Norte ─────────────────────────────────────────────────────────
    "San Isidro":           {"min": 2000, "max": 3200, "avg": 2500, "zona": "GBA Norte", "rentabilidad_pct": 4.5},
    "Vicente López":        {"min": 1800, "max": 2800, "avg": 2200, "zona": "GBA Norte", "rentabilidad_pct": 4.8},
    "Tigre":                {"min": 1200, "max": 2200, "avg": 1600, "zona": "GBA Norte", "rentabilidad_pct": 5.5},
    "Pilar":                {"min": 900,  "max": 1800, "avg": 1300, "zona": "GBA Norte", "rentabilidad_pct": 5.8},
    "San Fernando":         {"min": 1100, "max": 1800, "avg": 1400, "zona": "GBA Norte", "rentabilidad_pct": 5.6},
    "Nordelta":             {"min": 1800, "max": 3000, "avg": 2300, "zona": "GBA Norte", "rentabilidad_pct": 4.5},

    # ── GBA Oeste / Sur ────────────────────────────────────────────────────
    "La Matanza":           {"min": 700,  "max": 1200, "avg": 950,  "zona": "GBA Oeste", "rentabilidad_pct": 7.0},
    "Morón":                {"min": 900,  "max": 1500, "avg": 1150, "zona": "GBA Oeste", "rentabilidad_pct": 6.5},
    "Ramos Mejía":          {"min": 1000, "max": 1600, "avg": 1250, "zona": "GBA Oeste", "rentabilidad_pct": 6.3},
    "San Justo":            {"min": 800,  "max": 1300, "avg": 1050, "zona": "GBA Oeste", "rentabilidad_pct": 6.8},
    "Lanús":                {"min": 700,  "max": 1100, "avg": 900,  "zona": "GBA Sur",   "rentabilidad_pct": 7.2},
    "Lomas de Zamora":      {"min": 800,  "max": 1300, "avg": 1050, "zona": "GBA Sur",   "rentabilidad_pct": 7.0},
    "Quilmes":              {"min": 700,  "max": 1200, "avg": 950,  "zona": "GBA Sur",   "rentabilidad_pct": 7.1},
    "Avellaneda":           {"min": 750,  "max": 1250, "avg": 1000, "zona": "GBA Sur",   "rentabilidad_pct": 7.0},
}

# ── Expensas típicas por categoría de edificio ────────────────────────────────
# En ARS/mes (actualizar según inflación — Q1 2026)
EXPENSAS_TIPICAS_ARS: dict[str, dict] = {
    "Sin amenities (edificio viejo)":      {"min": 30_000,  "max": 80_000,  "avg": 55_000},
    "Con amenities básicos (SUM, quincho)":{"min": 80_000,  "max": 150_000, "avg": 115_000},
    "Premium (gym, pileta, seguridad 24h)":{"min": 150_000, "max": 350_000, "avg": 230_000},
    "Lujo / torre corporativa":            {"min": 300_000, "max": 700_000, "avg": 450_000},
}

# ── Tipo de cambio de referencia ──────────────────────────────────────────────
# Se actualiza en config.py/.env — acá solo el default orientativo
TC_BLUE_DEFAULT = 1_250   # ARS por USD (blue/informal, Q1 2026 — actualizar)
TC_OFICIAL_DEFAULT = 1_100  # ARS por USD (oficial BNA, Q1 2026)


# ── Gastos de escritura CABA 2026 ─────────────────────────────────────────────
# Porcentajes sobre el PRECIO DE ESCRITURA (precio real de la operación)
# Fuente: Colegio de Escribanos CABA + AFIP + ARBA
GASTOS_ESCRITURA: dict = {
    "comprador": {
        "sello_caba_pct": 0.0075,           # ITE CABA: 1.5% total, mitad a cargo del comprador
        "escribano_pct": 0.010,              # Honorarios escribano (comprador): ~1%
        "rpi_inscripcion_pct": 0.005,        # Registro de la Propiedad Inmueble: ~0.5%
        "estudio_juridico_pct": 0.005,       # Estudio jurídico / informe de dominio: ~0.5%
        "total_aprox_pct": 0.027,            # Total orientativo comprador: ~2.7%
        "descripcion": "Sello CABA + Escribano + RPI + Estudio jurídico",
    },
    "vendedor": {
        "sello_caba_pct": 0.0075,            # ITE CABA: mitad a cargo del vendedor
        "iti_afip_pct": 0.015,               # ITI AFIP: 1.5% (propiedades adquiridas antes de 2018)
        "escribano_pct": 0.005,              # Honorarios escribano (vendedor): ~0.5%
        "total_aprox_pct": 0.028,            # Total orientativo vendedor (sin ITI): ~1.3% / con ITI: ~2.8%
        "descripcion": "Sello CABA + Escribano + ITI (si aplica)",
        "nota": "El ITI (1.5%) aplica a propiedades adquiridas ANTES del 01/01/2018. "
                "Las posteriores tributan Ganancias sobre la ganancia real (15% escalonado).",
    },
}

# ── ReMax: tabla de comisiones ────────────────────────────────────────────────
REMAX_TABLAS: dict[str, float] = {
    "Tabla 45% (inicio)":   0.45,
    "Tabla 50%":            0.50,
    "Tabla 55%":            0.55,
    "Tabla 60% (estándar)": 0.60,
    "Tabla 65%":            0.65,
    "Tabla 70%":            0.70,
    "Tabla 75%":            0.75,
    "Tabla 80% (senior)":   0.80,
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_benchmark(barrio: str) -> dict | None:
    """Retorna el benchmark de m² para un barrio, o None si no está en la tabla."""
    return BENCHMARK_M2.get(barrio)


def get_barrios_list() -> list[str]:
    """Lista de todos los barrios disponibles, ordenados."""
    return sorted(BENCHMARK_M2.keys())


def get_barrios_by_zona() -> dict[str, list[str]]:
    """Agrupa barrios por zona (CABA, GBA Norte, etc.)."""
    result: dict[str, list[str]] = {}
    for barrio, data in BENCHMARK_M2.items():
        zona = data["zona"]
        result.setdefault(zona, []).append(barrio)
    return {k: sorted(v) for k, v in sorted(result.items())}


def ars_to_usd(ars: float, tc: float = TC_BLUE_DEFAULT) -> float:
    """Convierte ARS a USD usando el tipo de cambio indicado."""
    return round(ars / tc, 2) if tc > 0 else 0.0


def clasificar_precio_m2(precio_m2: float, barrio: str) -> tuple[str, str]:
    """
    Compara el precio/m² de una propiedad con el benchmark del barrio.
    Retorna (etiqueta, color_css).
    """
    bench = get_benchmark(barrio)
    if bench is None:
        return "Sin datos", "#888888"
    avg = bench["avg"]
    diff_pct = ((precio_m2 - avg) / avg) * 100
    if diff_pct <= -15:
        return f"Ganga ({diff_pct:+.0f}% vs. avg)", "#27ae60"
    elif diff_pct <= -5:
        return f"Bajo ({diff_pct:+.0f}% vs. avg)", "#2ecc71"
    elif diff_pct <= 5:
        return f"En línea ({diff_pct:+.0f}%)", "#f39c12"
    elif diff_pct <= 15:
        return f"Alto ({diff_pct:+.0f}% vs. avg)", "#e67e22"
    else:
        return f"Sobrevaluado ({diff_pct:+.0f}% vs. avg)", "#e74c3c"
