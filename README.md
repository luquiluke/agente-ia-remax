# 🏢 Agente IA ReMax Buenos Aires

[![License: MIT](https://img.shields.io/badge/License-MIT-green?logo=opensourceinitiative)](https://opensource.org/licenses/MIT)
![Status](https://img.shields.io/badge/Status-v1.0-brightgreen)
![Region](https://img.shields.io/badge/Región-Buenos_Aires-blue?logo=googlemaps)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-ff4b4b?logo=streamlit)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-black?logo=openai)](https://platform.openai.com/)

Suite de herramientas con IA para agentes inmobiliarios de **ReMax Buenos Aires**: scanner diario de oportunidades, calculadoras especializadas y asistente conversacional con conocimiento del mercado porteño.

> ⚠️ Uso informativo. Los datos de benchmarks son orientativos y no reemplazan el análisis profesional de cada operación.

---

## 🚀 Funcionalidades

### 🔍 Scanner de Oportunidades
- Escanea propiedades publicadas en ReMax Buenos Aires (modo live o demo)
- Calcula métricas de inversión por propiedad: precio/m² vs. benchmark del barrio, rentabilidad bruta y DOM
- Asigna un **Grade A–F** a cada oportunidad
- Genera un reporte ejecutivo con GPT-4o-mini
- Envía el reporte diario por email (Gmail SMTP)
- Exporta a Google Sheets

### 🧮 Calculadoras
Cuatro calculadoras especializadas para el mercado de CABA:
- **Comisión ReMax** — tabla 45%–80% con co-broke incluido
- **Gastos de escritura CABA 2026** — honorarios, sellado, ITI/Ganancias, escribano
- **Rentabilidad del inversor** — ROI, cap rate y flujo proyectado
- **Análisis de pozo / fideicomiso** — comparativa vs. mercado secundario

### 🤖 Asistente IA
- Chat en español rioplatense con conocimiento del mercado porteño
- Benchmarks USD/m² por barrio para CABA y GBA
- Estrategias de negociación, análisis de barrios y consultas sobre comisiones y escrituras

---

## 🧠 Tecnologías

- **Python 3.10+**
- **Streamlit 1.35+**
- **OpenAI GPT-4o-mini**
- **Playwright + BeautifulSoup4** para scraping
- **gspread + Google Auth** para Google Sheets
- **Pandas** para análisis de datos

---

## 📂 Estructura del proyecto

```
agente-ia-remax/
├── app.py                  # Home — branding ReMax y acceso a herramientas
├── config.py               # Settings con Pydantic (carga .env)
├── market_data.py          # Benchmarks USD/m² por barrio
├── calculators.py          # Lógica de las 4 calculadoras
├── investment_analyzer.py  # Motor de análisis de inversión
├── remax_scraper.py        # Scraper Playwright de ReMax BA
├── report_generator.py     # Generación de reporte con GPT
├── pages/
│   ├── 1_Scanner.py        # Página Scanner
│   ├── 2_Calculadoras.py   # Página Calculadoras
│   └── 3_Asistente.py      # Página Asistente IA
├── credentials/            # Service account Google (no commitear)
├── .env.example            # Plantilla de variables de entorno
├── requirements.txt
└── Dockerfile
```

---

## 🔐 Variables de entorno

Copiá `.env.example` a `.env` y completá los valores:

```bash
cp .env.example .env
```

| Variable | Descripción | Requerida |
|---|---|---|
| `OPENAI_API_KEY` | API Key de OpenAI | ✅ |
| `REMAX_EMAIL` / `REMAX_PASSWORD` | Credenciales para scraping live | Opcional |
| `GOOGLE_SHEETS_CREDENTIALS` | Path al service account JSON | Opcional |
| `GOOGLE_SPREADSHEET_ID` | ID del spreadsheet destino | Opcional |
| `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` | Para envío de reporte diario | Opcional |

> Sin Google Sheets ni Gmail configurados, la app funciona en **modo demo** con datos de muestra.

---

## ▶️ Cómo ejecutar

**Local:**
```bash
git clone https://github.com/luquiluke/agente-ia-remax.git
cd agente-ia-remax

python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium

cp .env.example .env
# Editá .env con tu OPENAI_API_KEY

streamlit run app.py
```

**Docker:**
```bash
docker build -t agente-remax .
docker run -p 8501:8501 --env-file .env agente-remax
```

La app queda disponible en `http://localhost:8501`.

---

## 🗺️ Cobertura de barrios

Benchmarks USD/m² disponibles para más de 40 barrios de CABA y GBA, organizados por zonas:

- **Premium:** Palermo, Belgrano, Recoleta, Núñez, Las Cañitas
- **Norte:** Vicente López, San Isidro, Olivos, Martínez
- **Centro:** San Telmo, Montserrat, Balvanera, Once
- **Oeste/Sur:** Caballito, Flores, Villa Crespo, Almagro, Boedo
- Entre otros

---

## 📄 Licencia

MIT — libre para uso y modificación.
