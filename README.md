# 🌿 EcoTrace | CARBONPULSE
### Campus Carbon Footprint Auditor (UN SDG 13: Climate Action)

> **"Measure. Understand. Reduce."**
>
> A campus sustainability & carbon footprint auditor for Indian educational institutions. Scans English, Marathi, and Hindi electricity bills, calculates CO₂ using CEA baseline factors, visualizes ₹ savings alongside carbon metrics, ranks departments fairly per student, and generates NAAC Criterion VII-ready sustainability reports.

---

## 🏛️ Architecture Overview

- **Frontend**: Premium SaaS dashboard built with HTML5, Vanilla CSS, and modern JavaScript with Chart.js, Lucide icons, responsive navigation, and hash-based SPA routing.
- **Backend**: FastAPI (Python 3.10+), SQLite / Supabase PostgreSQL, SQLAlchemy, Tesseract OCR (multilingual: English / Marathi / Hindi), ReportLab PDF engine.

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| 📊 **KPI Dashboard** | Real-time Total CO₂e, per-student emission, energy expenditure & net reduction |
| 📈 **Carbon Analytics** | Scope 1, Scope 2 & Scope 3 breakdowns with 6-month historical trends |
| 🏆 **Carbon League** | Departmental leaderboard normalized fairly by student head-count |
| 🔍 **OCR Bill Scanner** | Upload MSEDCL electricity bills with multilingual OCR extraction |
| ⚡ **Anomaly Detection** | Statistical Z-score based anomaly alerts for night baseload & power spikes |
| 🍱 **Mess Carbon Score** | Meal-level carbon intensity tracking with Green Day incentives |
| 🎚️ **What-If Simulator** | Interactive real-time sliders for PC shutdown, EV carpooling & solar ROI |
| ☀️ **Solar Timing Tip** | Intelligent load-shifting recommendations for peak solar generation hours |
| 🎯 **Actionable Recommendations** | ROI-backed initiatives with direct one-click simulation links |
| 📋 **NAAC / NIRF Reports** | One-click NAAC Criterion VII.1.2 Institutional Green Audit generator |

---

## 📁 Repository Structure

```
minihack/
├── index.html           # Main frontend SPA dashboard shell
├── styles.css           # Custom design system (forest-green theme)
├── app.js               # Client-side router, Chart.js integrations & simulators
├── README.md            # Project documentation
├── backend/             # FastAPI backend microservice
│   ├── main.py          # FastAPI application entrypoint
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic schemas
│   ├── seed.py          # Demo dataset seeder
│   ├── test_api.py      # Automated endpoint test suite
│   ├── requirements.txt # Python dependencies
│   ├── routers/         # Modular API routes (bills, mess, whatif, etc.)
│   └── services/        # Business logic (OCR, carbon calculation, PDF reports)
└── .gitignore
```

---

## 🚦 Getting Started

### 1. Frontend Dashboard (Quick Preview)

No build step required:
```bash
# Serve locally with Python HTTP server
python -m http.server 8080
```
Open **http://localhost:8080** in your web browser.

### 2. Backend API Service

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Seed demo database (6 months history + mess menu)
python seed.py

# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Open **http://localhost:8000/docs** to test all interactive OpenAPI endpoints.

---

## 🌍 UN SDG & NAAC Alignment

- **UN SDG 13 — Climate Action**: Facilitates real institutional carbon abatement through data transparency.
- **NAAC Criterion VII**: Automated metrics and PDF documentation for Green Campus and Energy Audit compliance.

---

*Built for Indian Campus Sustainability.*
