"""
config.py — Configuración centralizada del Agente IA de ReMax
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # ── OpenAI ────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # ── ReMax / Scraping ──────────────────────────────────────────────────────
    REMAX_EMAIL: str = os.getenv("REMAX_EMAIL", "")
    REMAX_PASSWORD: str = os.getenv("REMAX_PASSWORD", "")
    REMAX_TABLA: str = os.getenv("REMAX_TABLA", "0.60")          # % del bruto que retiene el agente
    COMISION_BRUTA_PCT: str = os.getenv("COMISION_BRUTA_PCT", "0.04")  # 4% default total

    # ── Google Sheets ─────────────────────────────────────────────────────────
    GOOGLE_SHEETS_CREDENTIALS: str = os.getenv(
        "GOOGLE_SHEETS_CREDENTIALS", "credentials/service_account.json"
    )
    GOOGLE_SPREADSHEET_ID: str = os.getenv("GOOGLE_SPREADSHEET_ID", "")
    PROPIEDADES_SHEET: str = os.getenv("PROPIEDADES_SHEET", "propiedades")
    DEALS_SHEET: str = os.getenv("DEALS_SHEET", "deals")
    CLIENTES_SHEET: str = os.getenv("CLIENTES_SHEET", "clientes")

    # ── Gmail SMTP ────────────────────────────────────────────────────────────
    GMAIL_ADDRESS: str = os.getenv("GMAIL_ADDRESS", "")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")
    REPORT_RECIPIENT_EMAIL: str = os.getenv("REPORT_RECIPIENT_EMAIL", "")

    # ── Google Calendar ───────────────────────────────────────────────────────
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")

    # ── Tipo de cambio (fallback si no hay API) ───────────────────────────────
    TC_BLUE: str = os.getenv("TC_BLUE", "1250")          # ARS por USD (blue)
    TC_OFICIAL: str = os.getenv("TC_OFICIAL", "1100")    # ARS por USD (oficial BNA)

    # ── Scanner ───────────────────────────────────────────────────────────────
    SCANNER_MAX_PROPIEDADES: int = int(os.getenv("SCANNER_MAX_PROPIEDADES", "50"))
    SCANNER_PRECIO_MIN_USD: int = int(os.getenv("SCANNER_PRECIO_MIN_USD", "50000"))
    SCANNER_PRECIO_MAX_USD: int = int(os.getenv("SCANNER_PRECIO_MAX_USD", "500000"))

    # ── Contraseña interna (modo agente) ─────────────────────────────────────
    INTERNAL_PASSWORD: str = os.getenv("INTERNAL_PASSWORD", "remax2026")

    # ── Propiedades calculadas ────────────────────────────────────────────────
    @property
    def remax_tabla_float(self) -> float:
        try:
            return float(self.REMAX_TABLA)
        except ValueError:
            return 0.60

    @property
    def comision_bruta_float(self) -> float:
        try:
            return float(self.COMISION_BRUTA_PCT)
        except ValueError:
            return 0.04

    @property
    def tc_blue_int(self) -> int:
        try:
            return int(self.TC_BLUE)
        except ValueError:
            return 1250

    @property
    def tc_oficial_int(self) -> int:
        try:
            return int(self.TC_OFICIAL)
        except ValueError:
            return 1100

    @property
    def google_configurado(self) -> bool:
        return bool(self.GOOGLE_SPREADSHEET_ID) and os.path.exists(
            self.GOOGLE_SHEETS_CREDENTIALS
        )

    @property
    def gmail_configurado(self) -> bool:
        return bool(self.GMAIL_ADDRESS) and bool(self.GMAIL_APP_PASSWORD)

    @property
    def remax_scraper_configurado(self) -> bool:
        return bool(self.REMAX_EMAIL) and bool(self.REMAX_PASSWORD)


settings = Settings()
