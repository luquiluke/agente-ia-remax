"""
remax_scraper.py — Scraper de propiedades ReMax Argentina
──────────────────────────────────────────────────────────
Modo 1 (live):  API JSON pública de ReMax Argentina (sin login)
                api-ar.redremax.com/remaxweb-ar/api/listings/findAll
Modo 2 (demo):  datos mock realistas de CABA (fallback si la API falla)

La app funciona sin credenciales: consulta ReMax en vivo y cae a demo
automáticamente si no hay conexión.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import date, datetime, timedelta

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


# ─── Scraper API pública de ReMax Argentina ──────────────────────────────────
# remax.com.ar es una SPA React respaldada por una API JSON pública (sin login).
# El front-end consume este endpoint; lo usamos directamente — es mucho más
# confiable que parsear el HTML renderizado o automatizar el login con Playwright.

REMAX_API_URL = "https://api-ar.redremax.com/remaxweb-ar/api/listings/findAll"
REMAX_API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "es-AR,es;q=0.9",
}

# operation.value → operacion normalizada
_OP_VALUE_MAP = {"sale": "Venta", "rent": "Alquiler"}
# type.value → tipo normalizado
_TIPO_VALUE_MAP = {
    "departamento": "Departamento", "casa": "Casa", "ph": "PH",
    "local": "Local", "terreno": "Terreno", "oficina": "Oficina",
    "cochera": "Cochera", "galpon": "Galpón", "campo": "Campo",
}
# operacion (input) → operationId del API
_OPERACION_ID = {"venta": 1, "alquiler": 2}

# Particiones GBA para inferir zona desde el partido (addressInfo)
_GBA_NORTE = {"vicente lopez", "san isidro", "tigre", "san fernando", "pilar",
              "escobar", "malvinas argentinas", "jose c paz", "san miguel"}
_GBA_OESTE = {"la matanza", "moron", "moreno", "merlo", "ituzaingo", "hurlingham",
              "tres de febrero", "general san martin", "san martin"}
_GBA_SUR = {"avellaneda", "lanus", "lomas de zamora", "quilmes", "berazategui",
            "florencio varela", "almirante brown", "esteban echeverria",
            "ezeiza", "presidente peron"}


def _zona_desde_address(address_info: str) -> str:
    """Infiere la zona (CABA / GBA Norte/Oeste/Sur) desde el addressInfo del API."""
    low = (address_info or "").lower()
    if "capital federal" in low:
        return "CABA"
    if "buenos aires" not in low:
        return "Otra"  # otra provincia (Córdoba, Santa Fe, etc.)
    partidos = [p.strip().lower() for p in low.split(",")]
    for p in partidos:
        if p in _GBA_NORTE:
            return "GBA Norte"
        if p in _GBA_OESTE:
            return "GBA Oeste"
        if p in _GBA_SUR:
            return "GBA Sur"
    return "GBA Norte"  # default razonable para Buenos Aires provincia


def _item_a_propiedad(it: dict) -> Optional[PropiedadRemax]:
    """Mapea un item del API de ReMax a PropiedadRemax. None si no es usable."""
    currency = (it.get("currency") or {}).get("value")
    precio = float(it.get("price") or 0)
    if currency != "USD" or precio <= 0:
        return None  # el scanner razona en USD; descartamos ARS / sin precio

    address_info = it.get("addressInfo") or ""
    barrio = address_info.split(",")[0].strip() if address_info else "Buenos Aires"

    superficie = (it.get("dimensionCovered")
                  or it.get("dimensionTotalBuilt")
                  or it.get("dimensionLand") or 0)

    expensas = it.get("expensesPrice") or 0
    expensas_cur = (it.get("expensesCurrency") or {}).get("value")

    rooms = int(it.get("totalRooms") or 0)
    assoc = it.get("associate") or {}
    emails = assoc.get("emails") or []
    slug = it.get("slug") or ""

    return PropiedadRemax(
        id=str(it.get("internalId") or it.get("id") or "")[:24],
        titulo=it.get("title") or "Propiedad ReMax",
        barrio=barrio,
        zona=_zona_desde_address(address_info),
        tipo=_TIPO_VALUE_MAP.get((it.get("type") or {}).get("value", ""), "Departamento"),
        operacion=_OP_VALUE_MAP.get((it.get("operation") or {}).get("value", ""), "Venta"),
        precio_usd=precio,
        superficie_m2=float(superficie or 0),
        ambientes=rooms,
        dormitorios=max(rooms - 1, 0),
        banos=int(it.get("bathrooms") or 0),
        expensas_ars=float(expensas) if expensas_cur == "ARS" else 0.0,
        antiguedad_anos=0,
        dias_en_mercado=0,  # el payload de listado no expone fecha de publicación
        url=f"https://www.remax.com.ar/listings/{slug}" if slug else "",
        agente_nombre=assoc.get("name", ""),
        agente_email=emails[0]["value"] if emails else "",
        descripcion=address_info,
    )


# ─── Días en mercado (DOM) por seguimiento local ──────────────────────────────
# El API de ReMax NO expone fecha de publicación (ordena por -createdAt pero no
# devuelve el valor). Para tener DOM real registramos cuándo vimos cada listing
# por primera vez y acumulamos. Empieza en 0 y se vuelve preciso a medida que el
# scanner corre día a día. (En Streamlit Cloud el filesystem es efímero, así que
# allí el historial puede reiniciarse entre deploys.)

_FIRST_SEEN_PATH = Path(__file__).parent / "data" / "listing_first_seen.json"


def _load_first_seen() -> dict:
    try:
        return json.loads(_FIRST_SEEN_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_first_seen(store: dict) -> None:
    try:
        _FIRST_SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        _FIRST_SEEN_PATH.write_text(json.dumps(store), encoding="utf-8")
    except Exception:
        pass  # sin persistencia (p.ej. FS de solo lectura) → DOM queda en 0


def _aplicar_dom(propiedades: list[PropiedadRemax]) -> None:
    """Asigna dias_en_mercado según la primera vez que vimos cada propiedad."""
    store = _load_first_seen()
    hoy = date.today()
    nuevos = False
    for p in propiedades:
        if not p.id:
            continue
        visto = store.get(p.id)
        if visto:
            try:
                p.dias_en_mercado = max((hoy - date.fromisoformat(visto)).days, 0)
                continue
            except ValueError:
                pass  # fecha corrupta → re-registrar
        store[p.id] = hoy.isoformat()
        p.dias_en_mercado = 0
        nuevos = True
    if nuevos:
        _save_first_seen(store)


def _scrape_api(
    barrios: list[str] | None = None,
    precio_min: int = 50_000,
    precio_max: int = 500_000,
    operacion: str = "venta",
    max_resultados: int = 50,
    page_cap: int = 12,
) -> list[PropiedadRemax]:
    """
    Trae propiedades desde la API pública de ReMax Argentina (sin login).

    El servidor ignora los filtros de precio y ubicación, así que paginamos
    sobre los listados más nuevos y filtramos en el cliente por precio y barrio.
    Retorna lista vacía si falla — la app cae a mock data.
    """
    try:
        import requests

        op_id = _OPERACION_ID.get((operacion or "venta").lower(), 1)
        barrios_lower = {b.lower() for b in barrios} if barrios else None
        page_size = 50
        out: list[PropiedadRemax] = []

        with requests.Session() as s:
            s.headers.update(REMAX_API_HEADERS)
            for page in range(page_cap):
                params = {
                    "page": page,
                    "pageSize": page_size,
                    "sort": "-createdAt",
                    "in:operationId": op_id,
                    "filterCount": 1,
                    "viewMode": "listViewMode",
                }
                resp = s.get(REMAX_API_URL, params=params, timeout=20)
                resp.raise_for_status()
                items = (resp.json().get("data") or {}).get("data") or []
                if not items:
                    break

                for it in items:
                    prop = _item_a_propiedad(it)
                    if prop is None:
                        continue
                    if not (precio_min <= prop.precio_usd <= precio_max):
                        continue
                    if barrios_lower and prop.barrio.lower() not in barrios_lower:
                        continue
                    out.append(prop)
                    if len(out) >= max_resultados:
                        _aplicar_dom(out)
                        return out

        _aplicar_dom(out)
        return out

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
        modo_usado: "live_api" | "demo"
    """
    precio_min = precio_min or settings.SCANNER_PRECIO_MIN_USD
    precio_max = precio_max or settings.SCANNER_PRECIO_MAX_USD
    max_resultados = max_resultados or settings.SCANNER_MAX_PROPIEDADES

    # "Pozo" no es una operación distinguible en el API → usamos los datos demo,
    # que sí incluyen unidades en pozo de ejemplo.
    if operacion and operacion.lower() == "pozo":
        mock = _generar_mock_propiedades()
        return _filtrar(mock, barrios, "pozo"), "demo"

    # Live: API pública de ReMax Argentina (sin login, ya filtra precio/barrio).
    resultados = _scrape_api(barrios, precio_min, precio_max, operacion, max_resultados)
    if resultados:
        return resultados, "live_api"

    # Fallback: datos demo.
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
