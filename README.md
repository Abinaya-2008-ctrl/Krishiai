# KrishiAI — Hyperlocal Crop Advisory & Farmer Benefits System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.35%2B-brightgreen.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-25%20Passed-success.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **College SDG Hackathon Project & GS-JTI Internship Portfolio Submission**  
> *Developed by a Computer Science & Engineering undergraduate student.*

---

## 1. Project Overview

**KrishiAI** is a transparent, explainable agricultural technology application designed to bridge the information gap for smallholder and marginal farmers in India, with primary focus on **Tamil Nadu**. 

Unlike generic agricultural chatbots that produce unverifiable recommendations or prototype dashboards filled with hardcoded demo metrics, KrishiAI provides **real, testable software functionality**:
- A local-first, privacy-respecting **SQLite data engine**
- An **explainable rule-based crop advisory engine** citing authentic agricultural manuals (ICAR, TNAU, KVK)
- A **Government Scheme Discovery and Verification module** that matches state and central schemes to farmer profiles, evaluates eligibility honestly, and directs farmers to verified official application portals
- **Hyperlocal weather forecasting** using Open-Meteo with provenance labeling
- A **crop growth calendar** tracking Days After Sowing (DAS) milestones
- **Market price transparency** with clear demarcation of demonstration benchmarks versus real farmer sale receipts

---

## 2. Problem Statement

Smallholder farmers (holding less than 2 hectares / 5 acres) make up over 86% of India's agricultural community. They face three chronic challenges:
1. **Uncertain Advisory Information:** Misleading chemical fertilizer or pesticide dosages sourced from commission agents without scientific validation or soil-context awareness.
2. **Low Scheme Awareness & Complex Portals:** Farmers miss out on 100% micro-irrigation subsidies, crop insurance windows, or DBT income transfers due to unannounced deadlines and difficulty finding legitimate government portals amidst unofficial third-party sites.
3. **Data Inauthenticity:** Digital farm tools often present fabricated yield increases, sensor graphs, or artificial AI predictions that fail under real field conditions.

---

## 3. Target Users

- **Marginal & Small Farmers (< 5 acres):** Needing verified government subsidy assistance, planting schedules, and organic/IPM pest alerts.
- **Tenant & Sharecropper Farmers:** Needing clear guidance on which schemes permit tenancy agreements (e.g. PMFBY crop insurance) versus those requiring registered land ownership (e.g. PM-KISAN).
- **Agricultural Field Officers & Students:** Seeking an open, extensible, and explainable software architecture for farm advisory systems.

---

## 4. Key Functional Modules

| Module | Core Functionality | Data Provenance Label |
|---|---|---|
| **🌾 Dashboard** | Displays live weather, farm summary metrics, urgent calendar tasks, and high-priority schemes. | Clear tag per card (`LIVE_DATA`, `CALCULATED_ESTIMATE`, etc.) |
| **🌱 My Fields** | Multi-parcel land registry with fractional acre support, sowing date tracking, and cascading deletion in SQLite. | `FARMER-ENTERED` |
| **📖 Crop Advisory** | Hyperlocal, explainable recommendations citing **ICAR**, **TNAU Agritech Portal**, and **KVK** with growth stages and risk disclaimers. | `EXPLAINABLE_RULE_BASED` |
| **📅 Crop Calendar** | Tracks Days After Sowing (DAS), stage milestones, checklist toggling, and custom reminder scheduling. | `CALCULATED_ESTIMATE` & `FARMER-ENTERED` |
| **📈 Market Intelligence** | APMC regulated market price benchmarks, links to official **Agmarknet**, and a personal farm sales transaction ledger. | `DEMONSTRATION_BENCHMARK` vs `FARMER_RECORD` |
| **🏛️ Govt Schemes (Core)** | Matches Central and Tamil Nadu government schemes against farmer profiles (landholding, crop, tenancy, district). Shows verified deadlines and links directly to official government portals (`tnagrisnet.tn.gov.in`, `pmkisan.gov.in`). | `VERIFIED_OFFICIAL` |
| **📊 Impact Report** | Calculates real farm metrics: fields registered, tasks completed, actual expenses recorded, and sales revenue. **Zero fabricated statistics.** | `CALCULATED_ESTIMATE` |
| **⚙️ Settings & Privacy** | Local profile editing, English/Tamil language selector, CSV data export, and complete local database purge. | Local device storage |

---

## 5. Technology Stack

- **Application Logic & Backend:** Python 3.10+ / 3.14
- **Interactive UI Framework:** [Streamlit](https://streamlit.io/)
- **Data Persistence:** [SQLite3](https://www.sqlite.org/) (Embedded relational database, zero cloud dependency)
- **Data Analysis & Export:** [Pandas](https://pandas.pydata.org/)
- **Visualisations:** [Plotly](https://plotly.com/) & Streamlit Native Metrics
- **Automated Testing:** [pytest](https://docs.pytest.org/) (25 unit and integration tests)
- **External Meteorological API:** [Open-Meteo](https://open-meteo.com/) (Free, non-commercial attribution tier, CC-BY 4.0)

---

## 6. Architecture & Database Schema

```
krishiai/
├── .streamlit/
│   └── config.toml             # Custom agricultural green theme
├── data/
│   ├── schemes.json            # Curated, verified Central & TN government schemes dataset
│   ├── advisory_rules.json     # Curated ICAR / TNAU crop advisory rules
│   └── sample_mandi_data.json  # Agmarknet / APMC benchmark prices
├── src/
│   ├── __init__.py
│   ├── config.py               # Constants, TN districts (38), seasons, land classification
│   ├── database.py             # SQLite connection, migrations, and CRUD operations
│   ├── weather_service.py      # Open-Meteo API client with caching, WMO codes & offline handling
│   ├── advisory_engine.py      # Explainable rule-matching engine citing ICAR & TNAU
│   ├── calendar_service.py     # Crop growth stages, DAS calculations, task generator
│   ├── market_service.py       # APMC mandi data viewer & farmer sales recorder
│   ├── scheme_engine.py        # Scheme eligibility matcher & official portal URL validator
│   ├── impact_calculator.py    # Genuine farm statistics calculator (no inflated claims)
│   ├── ui_components.py        # AgroBloom-styled cards, frosted pills, and provenance badges
│   └── translations.py         # English and Tamil localized strings
├── tests/
│   ├── test_database.py        # SQLite persistence and cascade tests
│   ├── test_scheme_engine.py   # Scheme matching, eligibility, and deadline tests
│   ├── test_advisory_engine.py # Rule matching and weather trigger tests
│   ├── test_weather_service.py # Weather geocoding and caching tests
│   ├── test_calendar_service.py# DAS progression tests
│   └── test_impact_calculator.py# Authentic impact aggregation tests
├── app.py                      # Main Streamlit application
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

### Relational Database Schema (SQLite)

```
+--------------------+       +--------------------+       +--------------------+
|   farmer_profile   |       |       fields       |       |   calendar_tasks   |
+--------------------+       +--------------------+       +--------------------+
| id (PK, =1)        |       | id (PK, Auto)      |1    * | id (PK, Auto)      |
| farmer_name        |       | field_name         +-------+ field_id (FK)      |
| preferred_language |       | crop               |       | crop               |
| state, district    |       | variety            |       | task_name          |
| total_land_acres   |       | area_acres         |       | growth_stage       |
| land_arrangement   |       | sowing_date        |       | scheduled_date     |
| irrigation_type    |       | irrigation_type    |       | is_completed       |
| current_season     |       | soil_type, notes   |       | is_custom          |
+--------------------+       +--------------------+       +--------------------+
                                       |
                                       |1
                                       |*
                             +--------------------+       +--------------------+
                             |    farm_records    |       |   saved_schemes    |
                             +--------------------+       +--------------------+
                             | id (PK, Auto)      |       | id (PK, Auto)      |
                             | field_id (FK)      |       | scheme_id (Unique) |
                             | record_type        |       | scheme_name        |
                             | amount_inr         |       | application_status |
                             | quantity_kg        |       | docs_checklist     |
                             | record_date        |       | reminder_date      |
                             +--------------------+       +--------------------+
```

---

## 7. Installation & Setup

### Prerequisites
- Python 3.10 or higher installed on your system.
- Git (optional, for cloning).

### Step 1: Clone or Open the Project Directory
```powershell
cd "C:\Users\ABINAYA K\.gemini\antigravity\scratch\krishiai"
```

### Step 2: Create a Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

---

## 8. How to Run the Application

Launch the Streamlit web server:
```powershell
streamlit run app.py
```

The application will automatically open in your web browser at:
`http://localhost:8501`

---

## 9. Running Automated Tests

Run the complete test suite with verbose output:
```powershell
python -m pytest tests -v
```

All 25 automated tests verify:
- Scheme matching across districts and crops
- Small (< 5.0 acres) and marginal (< 2.5 acres) land filtering
- Disqualification of tenant farmers on ownership-restricted schemes
- Expiry and validity checking of scheme deadlines
- Safe reachability and official domain validation (`gov.in`, `nic.in`, `tn.gov.in`)
- SQLite database integrity, cascade deletions, and data purges
- Explainable rule-based advisory triggers during rainfall events
- Calculation of authentic impact metrics without fabricated statistics

---

## 10. Data Sources & Scientific Attribution

1. **Crop Production Guidelines:**
   - **TNAU Agritech Portal** — Tamil Nadu Agricultural University, Coimbatore (Crop Production Guides for Paddy, Cotton, Groundnut, Sugarcane, Vegetables).
   - **ICAR-CRIDA** — Central Research Institute for Dryland Agriculture (Agromet Advisories).
   - **ICAR-NRCB** — National Research Centre for Banana, Tiruchirappalli.
   - **ICAR-CICR** — Central Institute for Cotton Research, Coimbatore.
2. **Government Schemes:**
   - **Department of Agriculture & Farmers Welfare, Govt of Tamil Nadu:** [TNAgrisnet Schemes Portal](https://www.tnagrisnet.tn.gov.in/home/schemes/)
   - **Tamil Nadu e-Sevai Service Portal:** [TNAgrisnet e-Sevai](https://www.tnagrisnet.tn.gov.in/esevai/)
   - **National Portal for Schemes Discovery:** [myScheme](https://www.myscheme.gov.in/)
   - **PM-KISAN Central Portal:** [pmkisan.gov.in](https://pmkisan.gov.in/)
   - **PMFBY Central Portal:** [pmfby.gov.in](https://pmfby.gov.in/)
3. **Hyperlocal Weather:**
   - **Open-Meteo API:** Free and open-source weather API under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## 11. Honest Disclaimers & Current Limitations

- **Student Prototype Notice:** This project was developed by a beginner CSE student for an SDG hackathon and internship application. It is a working functional software system, but not an official government deployment.
- **Rule-Based Advisories vs AI Diagnosis:** KrishiAI uses **transparent, documented agricultural rules** rather than black-box machine learning models. It does not fabricate disease diagnoses from photos. In cases of severe pest infestation or crop disease, farmers are always advised to contact their local Assistant Agricultural Officer (AAO) or Krishi Vigyan Kendra (KVK).
- **Government Application Submission:** KrishiAI does **not** process financial grants or directly submit official government applications. It guides farmers to official government portals (`tnagrisnet.tn.gov.in`, `pmkisan.gov.in`) where actual biometric/Aadhaar applications occur.
- **Market Prices:** Live mandi prices fluctuate daily based on auctions. Benchmark figures provided in the intelligence module are clearly labeled `DEMONSTRATION_BENCHMARK`, with direct links to the official Agmarknet portal.

---

## 12. Future Improvements

- [ ] Integration with Bhashini API for voice-based Tamil audio query responses.
- [ ] Direct Agmarknet API integration when public API credentials are released.
- [ ] Migration of the Streamlit frontend to React + FastAPI for high-concurrency mobile deployment.
- [ ] Integration of offline SQLite synchronization for remote rural connectivity.

---

## 13. License

Distributed under the MIT License. See `LICENSE` for details.
