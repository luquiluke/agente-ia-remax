"""
remax_scraper.py — Scraper de propiedades ReMax Argentina
──────────────────────────────────────────────────────────
Modo 1 (autenticado): Playwright con login en remax.com.ar
Modo 2 (público):     requests + BeautifulSoup sobre listados públicos
Modo 3 (demo):        datos mock realistas de CABA (siempre disponible)

La app funciona en modo demo sin credenciales.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta

from config import settings


# ─── Modelo de datos ──────────────────────────────────────────────────────────

@dataclass
class PropiedadRemax:
    """Una propiedad de ReMax Argentina normalizada."""
    id: str
    titulo: str
    barrio: str
    zona: str                        # CABA / GBA Norte / GBA Oeste / GBA Sur
    tipo: str                        # Departamento / Casa / PH / Local / Terreno
    operacion: str                   # Venta / Alquiler / Pozo
    precio_usd: float
    superficie_m2: float
    ambientes: int
    dormitorios: int
    banos: int
    expensas_ars: float              # 0 si no aplica
    antiguedad_anos: int             # 0 = estrenar/pozo
    amenities: list[str] = field(default_factory=list)
    piso: Optional[int] = None
    cochera: bool = False
    url: str = ""
    foto_url: str = ""
    agente_nombre: str = ""
    agente_email: str = ""
    dias_en_mercado: int = 0
    descripcion: str = ""
    es_pozo: bool = False
    entrega_estimada: Optional[str] = None  # "Q3 2026"

    # ── Calculados al crear el objeto ─────────────────────────────────────────
    @property
    def precio_m2_usd(self) -> float:
        if self.superficie_m2 > 0:
            return round(self.precio_usd / self.superficie_m2, 0)
        return 0.0

    @property
    def expensas_usd(self) -> float:
        """Expensas en USD usando TC blue default."""
        return round(self.expensas_ars / settings.tc_blue_int, 2)


# ─── Mock data ────────────────────────────────────────────────────────────────

def _generar_mock_propiedades() -> list[PropiedadRemax]:
    """
    15 propiedades mock realistas de CABA + GBA para modo demo.
    Semilla fija para reproducibilidad.
    """
    rng = random.Random(2026)

    def rnd(a: float, b: float) -> float:
        return round(rng.uniform(a, b), 0)

    propiedades_base = [
        # ── Palermo ──────────────────────────────────────────────────────────
        {
            "id": "RM-00101",
            "titulo": "Moderno 2 amb. con balcón — Palermo Soho",
            "barrio": "Palermo",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Venta",
            "precio_usd": 148_000,
            "superficie_m2": 52,
            "ambientes": 2,
            "dormitorios": 1,
            "banos": 1,
            "expensas_ars": 120_000,
            "antiguedad_anos": 8,
            "amenities": ["SUM", "Laundry"],
            "piso": 4,
            "cochera": False,
            "dias_en_mercado": 18,
            "descripcion": "Excelente 2 ambientes, luminoso, balcón corrido, cocina americana. Edificio con SUM.",
        },
        {
            "id": "RM-00102",
            "titulo": "PH 3 amb. con terraza privada — Palermo Hollywood",
            "barrio": "Soho / Palermo Hollywood",
            "zona": "CABA",
            "tipo": "PH",
            "operacion": "Venta",
            "precio_usd": 265_000,
            "superficie_m2": 95,
            "ambientes": 3,
            "dormitorios": 2,
            "banos": 2,
            "expensas_ars": 85_000,
            "antiguedad_anos": 15,
            "amenities": [],
            "piso": None,
            "cochera": True,
            "dias_en_mercado": 45,
            "descripcion": "PH de categoría, amplia terraza propia, quincho, 2 cocheras. Ideal para familia.",
        },
        # ── Recoleta ─────────────────────────────────────────────────────────
        {
            "id": "RM-00201",
            "titulo": "Clásico 3 amb. en edificio de categoría — Recoleta",
            "barrio": "Recoleta",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Venta",
            "precio_usd": 320_000,
            "superficie_m2": 98,
            "ambientes": 3,
            "dormitorios": 2,
            "banos": 2,
            "expensas_ars": 230_000,
            "antiguedad_anos": 40,
            "amenities": ["Portería 24h", "Salón de usos múltiples"],
            "piso": 7,
            "cochera": True,
            "dias_en_mercado": 62,
            "descripcion": "Clásico departamento en Recoleta, pisos de madera, techos altos, 2 cocheras.",
        },
        # ── Belgrano ─────────────────────────────────────────────────────────
        {
            "id": "RM-00301",
            "titulo": "Estrenar 2 amb. con amenities completos — Belgrano R",
            "barrio": "Belgrano",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Venta",
            "precio_usd": 175_000,
            "superficie_m2": 60,
            "ambientes": 2,
            "dormitorios": 1,
            "banos": 1,
            "expensas_ars": 185_000,
            "antiguedad_anos": 0,
            "amenities": ["Gym", "Pileta", "Seguridad 24h", "SUM", "Rooftop"],
            "piso": 9,
            "cochera": False,
            "dias_en_mercado": 5,
            "descripcion": "A estrenar, torre premium en Belgrano R, amenities de primer nivel, vistas panorámicas.",
        },
        # ── Caballito ─────────────────────────────────────────────────────────
        {
            "id": "RM-00401",
            "titulo": "Luminoso 3 amb. — Caballito Norte",
            "barrio": "Caballito",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Venta",
            "precio_usd": 145_000,
            "superficie_m2": 78,
            "ambientes": 3,
            "dormitorios": 2,
            "banos": 1,
            "expensas_ars": 95_000,
            "antiguedad_anos": 22,
            "amenities": ["SUM"],
            "piso": 3,
            "cochera": False,
            "dias_en_mercado": 30,
            "descripcion": "Amplio 3 ambientes, doble balcón, planta baja con sum. A pasos del Parque Rivadavia.",
        },
        {
            "id": "RM-00402",
            "titulo": "Monoambiente inversor — Caballito",
            "barrio": "Caballito",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Venta",
            "precio_usd": 72_000,
            "superficie_m2": 32,
            "ambientes": 1,
            "dormitorios": 0,
            "banos": 1,
            "expensas_ars": 60_000,
            "antiguedad_anos": 5,
            "amenities": ["Laundry"],
            "piso": 6,
            "cochera": False,
            "dias_en_mercado": 12,
            "descripcion": "Monoambiente nuevo, ideal inversión renta, alta demanda de alquiler en la zona.",
        },
        # ── Villa Crespo ──────────────────────────────────────────────────────
        {
            "id": "RM-00501",
            "titulo": "PH con jardín privado — Villa Crespo",
            "barrio": "Villa Crespo",
            "zona": "CABA",
            "tipo": "PH",
            "operacion": "Venta",
            "precio_usd": 195_000,
            "superficie_m2": 85,
            "ambientes": 3,
            "dormitorios": 2,
            "banos": 2,
            "expensas_ars": 70_000,
            "antiguedad_anos": 10,
            "amenities": [],
            "piso": None,
            "cochera": False,
            "dias_en_mercado": 21,
            "descripcion": "PH con jardín de 30m² propio, 2 dormitorios en suite, amplio living-comedor.",
        },
        # ── San Telmo ─────────────────────────────────────────────────────────
        {
            "id": "RM-00601",
            "titulo": "Loft reciclado en casona histórica — San Telmo",
            "barrio": "San Telmo",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Venta",
            "precio_usd": 118_000,
            "superficie_m2": 55,
            "ambientes": 2,
            "dormitorios": 1,
            "banos": 1,
            "expensas_ars": 55_000,
            "antiguedad_anos": 90,
            "amenities": [],
            "piso": 1,
            "cochera": False,
            "dias_en_mercado": 88,
            "descripcion": "Loft en casona histórica reciclada, techos de 4m, ladrillo visto, detalles únicos.",
        },
        # ── Villa Urquiza ─────────────────────────────────────────────────────
        {
            "id": "RM-00701",
            "titulo": "Casa 4 amb. con parque — Villa Urquiza",
            "barrio": "Villa Urquiza",
            "zona": "CABA",
            "tipo": "Casa",
            "operacion": "Venta",
            "precio_usd": 310_000,
            "superficie_m2": 180,
            "ambientes": 4,
            "dormitorios": 3,
            "banos": 3,
            "expensas_ars": 0,
            "antiguedad_anos": 35,
            "amenities": [],
            "piso": None,
            "cochera": True,
            "dias_en_mercado": 55,
            "descripcion": "Casa amplia, jardín de 200m², 3 dormitorios, quincho, garage. Barrio consolidado.",
        },
        # ── Pozo / fideicomiso ────────────────────────────────────────────────
        {
            "id": "RM-00801",
            "titulo": "En pozo — 2 amb. torre LEED — Palermo",
            "barrio": "Palermo",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Pozo",
            "precio_usd": 135_000,
            "superficie_m2": 54,
            "ambientes": 2,
            "dormitorios": 1,
            "banos": 1,
            "expensas_ars": 0,
            "antiguedad_anos": 0,
            "amenities": ["Gym", "Pileta", "Coworking", "Bicicletero", "Rooftop"],
            "piso": 12,
            "cochera": False,
            "dias_en_mercado": 3,
            "es_pozo": True,
            "entrega_estimada": "Q2 2027",
            "descripcion": "Unidad en pozo fideicomiso al costo, torre con certificación LEED, entrega Q2/2027. 30% adelanto + cuotas en USD.",
        },
        {
            "id": "RM-00802",
            "titulo": "En pozo — 3 amb. con cochera — Núñez",
            "barrio": "Núñez",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Pozo",
            "precio_usd": 215_000,
            "superficie_m2": 82,
            "ambientes": 3,
            "dormitorios": 2,
            "banos": 2,
            "expensas_ars": 0,
            "antiguedad_anos": 0,
            "amenities": ["SUM", "Gym", "Pileta", "Seguridad 24h"],
            "piso": 8,
            "cochera": True,
            "dias_en_mercado": 7,
            "es_pozo": True,
            "entrega_estimada": "Q4 2026",
            "descripcion": "Pozo con cochera incluida, zona premium Núñez, a 3 cuadras del Río. Entrega Q4/2026.",
        },
        # ── GBA Norte ─────────────────────────────────────────────────────────
        {
            "id": "RM-01001",
            "titulo": "Casa con pileta en barrio cerrado — Nordelta",
            "barrio": "Nordelta",
            "zona": "GBA Norte",
            "tipo": "Casa",
            "operacion": "Venta",
            "precio_usd": 480_000,
            "superficie_m2": 320,
            "ambientes": 5,
            "dormitorios": 4,
            "banos": 4,
            "expensas_ars": 450_000,
            "antiguedad_anos": 12,
            "amenities": ["Pileta privada", "Quincho", "Seguridad 24h"],
            "piso": None,
            "cochera": True,
            "dias_en_mercado": 75,
            "descripcion": "Casa premium en Nordelta, pileta propia, quincho, 4 dormitorios en suite, triple cochera.",
        },
        {
            "id": "RM-01002",
            "titulo": "Departamento 2 amb. — San Isidro centro",
            "barrio": "San Isidro",
            "zona": "GBA Norte",
            "tipo": "Departamento",
            "operacion": "Venta",
            "precio_usd": 155_000,
            "superficie_m2": 62,
            "ambientes": 2,
            "dormitorios": 1,
            "banos": 1,
            "expensas_ars": 130_000,
            "antiguedad_anos": 18,
            "amenities": ["Portería"],
            "piso": 2,
            "cochera": False,
            "dias_en_mercado": 40,
            "descripcion": "Buena ubicación en San Isidro centro, a pasos del tren y la catedral.",
        },
        # ── GBA Oeste ─────────────────────────────────────────────────────────
        {
            "id": "RM-01101",
            "titulo": "Casa 3 dorm. — Ramos Mejía",
            "barrio": "Ramos Mejía",
            "zona": "GBA Oeste",
            "tipo": "Casa",
            "operacion": "Venta",
            "precio_usd": 165_000,
            "superficie_m2": 200,
            "ambientes": 4,
            "dormitorios": 3,
            "banos": 2,
            "expensas_ars": 0,
            "antiguedad_anos": 28,
            "amenities": [],
            "piso": None,
            "cochera": True,
            "dias_en_mercado": 50,
            "descripcion": "Casa amplia con jardín, garage y quincho. Barrio tranquilo, a 10 min de Capital.",
        },
        # ── Oportunidad Flores ────────────────────────────────────────────────
        {
            "id": "RM-00901",
            "titulo": "Oportunidad 2 amb. a reciclar — Flores",
            "barrio": "Flores",
            "zona": "CABA",
            "tipo": "Departamento",
            "operacion": "Venta",
            "precio_usd": 68_000,
            "superficie_m2": 55,
            "ambientes": 2,
            "dormitorios": 1,
            "banos": 1,
            "expensas_ars": 45_000,
            "antiguedad_anos": 50,
            "amenities": [],
            "piso": 1,
            "cochera": False,
            "dias_en_mercado": 110,
            "descripcion": "Precio muy por debajo del barrio, requiere reciclaje. Excelente oportunidad para inversor.",
        },
    ]

    propiedades = []
    for data in propiedades_base:
        p = PropiedadRemax(**{k: v for k, v in data.items() if k in PropiedadRemax.__dataclass_fields__})
        propiedades.append(p)

    return propiedades


# ─── Scraper público (requests + BS4) ────────────────────────────────────────

def _scrape_publico(
    barrios: list[str] | None = None,
    precio_min: int = 50_000,
    precio_max: int = 500_000,
    tipo: str = "departamento",
    max_resultados: int = 30,
) -> list[PropiedadRemax]:
    """
    Scraping público de remax.com.ar (sin login).
    Retorna lista vacía si falla — la app cae a mock data.
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-AR,es;q=0.9",
        }

        # URL base de listados públicos ReMax Argentina
        base_url = "https://www.remax.com.ar/listings/buy"
        params = {
            "pageNumber": 0,
            "pageSize": min(max_resultados, 24),
            "sort": "NEWEST",
            "lang": "es-AR",
        }
        if precio_min:
            params["priceMin"] = precio_min
        if precio_max:
            params["priceMax"] = precio_max

        resp = requests.get(base_url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()

        # ReMax usa carga dinámica (React) — el scraping estático captura poco.
        # Para resultados completos, usar el modo Playwright autenticado.
        soup = BeautifulSoup(resp.text, "html.parser")

        # Intenta parsear las tarjetas si la carga estática incluye datos
        resultados: list[PropiedadRemax] = []
        tarjetas = soup.select("[data-testid='listing-card']")

        for i, tarjeta in enumerate(tarjetas[:max_resultados]):
            try:
                titulo_el = tarjeta.select_one("h2, .listing-title, [data-testid='listing-title']")
                precio_el = tarjeta.select_one(".listing-price, [data-testid='listing-price']")
                # Parseo básico — se expande según estructura real del HTML
                titulo = titulo_el.get_text(strip=True) if titulo_el else f"Propiedad {i+1}"
                precio_texto = precio_el.get_text(strip=True) if precio_el else "USD 0"
                precio = float("".join(c for c in precio_texto if c.isdigit() or c == ".") or 0)

                resultados.append(PropiedadRemax(
                    id=f"RM-WEB-{i+1:04d}",
                    titulo=titulo,
                    barrio=barrios[0] if barrios else "CABA",
                    zona="CABA",
                    tipo="Departamento",
                    operacion="Venta",
                    precio_usd=precio,
                    superficie_m2=0,
                    ambientes=0,
                    dormitorios=0,
                    banos=0,
                    expensas_ars=0,
                    antiguedad_anos=0,
                    dias_en_mercado=0,
                    url=resp.url,
                ))
            except Exception:
                continue

        return resultados

    except Exception:
        return []


# ─── Scraper autenticado (Playwright) ────────────────────────────────────────

def _scrape_autenticado(
    barrios: list[str] | None = None,
    precio_min: int = 50_000,
    precio_max: int = 500_000,
    max_resultados: int = 50,
) -> list[PropiedadRemax]:
    """
    Scraping con sesión autenticada usando Playwright.
    Requiere REMAX_EMAIL y REMAX_PASSWORD en .env.
    """
    if not settings.remax_scraper_configurado:
        return []

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            ctx = browser.new_context(locale="es-AR")
            page = ctx.new_page()

            # 1. Login
            page.goto("https://www.remax.com.ar/login", timeout=30_000)
            page.fill("input[name='email']", settings.REMAX_EMAIL)
            page.fill("input[name='password']", settings.REMAX_PASSWORD)
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle", timeout=15_000)

            # 2. Navegar al portal de propiedades
            page.goto(
                f"https://www.remax.com.ar/listings/buy"
                f"?priceMin={precio_min}&priceMax={precio_max}",
                timeout=30_000,
            )
            page.wait_for_load_state("networkidle", timeout=15_000)

            # 3. Scraping de tarjetas
            resultados: list[PropiedadRemax] = []
            tarjetas = page.query_selector_all("[data-testid='listing-card']")

            for i, tarjeta in enumerate(tarjetas[:max_resultados]):
                try:
                    titulo = tarjeta.query_selector("h2")
                    precio = tarjeta.query_selector("[data-testid='listing-price']")
                    superficie = tarjeta.query_selector("[data-testid='listing-surface']")
                    barrio_el = tarjeta.query_selector("[data-testid='listing-location']")
                    url_el = tarjeta.query_selector("a")

                    titulo_txt = titulo.inner_text() if titulo else f"Propiedad {i+1}"
                    precio_txt = precio.inner_text() if precio else "USD 0"
                    sup_txt = superficie.inner_text() if superficie else "0 m²"
                    barrio_txt = barrio_el.inner_text() if barrio_el else "Buenos Aires"
                    href = url_el.get_attribute("href") if url_el else ""

                    precio_val = float("".join(c for c in precio_txt if c.isdigit() or c == ".") or 0)
                    sup_val = float("".join(c for c in sup_txt if c.isdigit() or c == ".") or 0)

                    resultados.append(PropiedadRemax(
                        id=f"RM-LIVE-{i+1:04d}",
                        titulo=titulo_txt,
                        barrio=barrio_txt.split(",")[0].strip(),
                        zona="CABA",
                        tipo="Departamento",
                        operacion="Venta",
                        precio_usd=precio_val,
                        superficie_m2=sup_val,
                        ambientes=0,
                        dormitorios=0,
                        banos=0,
                        expensas_ars=0,
                        antiguedad_anos=0,
                        dias_en_mercado=0,
                        url=f"https://www.remax.com.ar{href}" if href else "",
                    ))
                except Exception:
                    continue

            browser.close()
            return resultados

    except Exception:
        return []


# ─── Función principal ────────────────────────────────────────────────────────

def buscar_propiedades(
    barrios: list[str] | None = None,
    precio_min: int | None = None,
    precio_max: int | None = None,
    tipo: str = "departamento",
    operacion: str = "venta",
    max_resultados: int | None = None,
) -> tuple[list[PropiedadRemax], str]:
    """
    Busca propiedades usando el mejor método disponible.

    Retorna:
        (lista_propiedades, modo_usado)
        modo_usado: "live_auth" | "live_publico" | "demo"
    """
    precio_min = precio_min or settings.SCANNER_PRECIO_MIN_USD
    precio_max = precio_max or settings.SCANNER_PRECIO_MAX_USD
    max_resultados = max_resultados or settings.SCANNER_MAX_PROPIEDADES

    # Intento 1: scraping autenticado
    if settings.remax_scraper_configurado:
        resultados = _scrape_autenticado(barrios, precio_min, precio_max, max_resultados)
        if resultados:
            return _filtrar(resultados, barrios, operacion), "live_auth"

    # Intento 2: scraping público
    resultados = _scrape_publico(barrios, precio_min, precio_max, tipo, max_resultados)
    if resultados:
        return _filtrar(resultados, barrios, operacion), "live_publico"

    # Fallback: mock data
    mock = _generar_mock_propiedades()
    return _filtrar(mock, barrios, operacion), "demo"


def _filtrar(
    propiedades: list[PropiedadRemax],
    barrios: list[str] | None,
    operacion: str,
) -> list[PropiedadRemax]:
    """Aplica filtros de barrio y tipo de operación."""
    resultado = propiedades

    if barrios:
        barrios_lower = [b.lower() for b in barrios]
        resultado = [p for p in resultado if p.barrio.lower() in barrios_lower]

    if operacion and operacion.lower() != "todos":
        op_map = {
            "venta": "Venta",
            "alquiler": "Alquiler",
            "pozo": "Pozo",
        }
        op_norm = op_map.get(operacion.lower(), operacion)
        resultado = [p for p in resultado if p.operacion == op_norm]

    return resultado
