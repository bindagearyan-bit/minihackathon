# Campus Carbon Footprint Auditor (UN SDG 13: Climate Action)

> Campus carbon auditor for Indian colleges. Scans English, Marathi, and Hindi electricity bills, calculates CO₂ using CEA baseline factors, shows ₹ savings alongside carbon metrics, ranks departments fairly per student, and generates NAAC-ready sustainability reports.

---

## Architecture Overview

- **Backend**: FastAPI (Python 3.10+), SQLite / Supabase PostgreSQL, SQLAlchemy, Tesseract OCR (multilingual), ReportLab PDF engine.
- **Frontend**: React (built separately, connecting via clean JSON REST APIs under `/api`).

---

## Quickstart (Backend)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed demo database with 6 months of data & mess menu
python seed.py

# 4. Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/docs** in your browser to view and test all interactive API documentation.

For detailed setup instructions, API endpoint reference, and mathematical formulas, please see the [backend/README.md](backend/README.md).
