# main.py - Main entry point for the Campus Carbon Auditor backend application.
# Configures FastAPI, CORS for React frontend integration, database tables, and registers all routers.

import os
import sys

# Ensure backend directory is in sys.path so imports work from root or inside backend
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models  # Ensures models are imported so tables are created

# Import all feature routers
from routers.bills import router as bills_router
from routers.overview import router as overview_router
from routers.whatif import router as whatif_router
from routers.leaderboard import router as leaderboard_router
from routers.mess import router as mess_router
from routers.reports import router as reports_router
from routers.anomalies import router as anomalies_router
from routers.tips import router as tips_router

from fastapi.staticfiles import StaticFiles

# Ensure storage directories exist for uploaded bills, reports, and static assets
os.makedirs(os.path.join(backend_dir, "uploads"), exist_ok=True)
os.makedirs(os.path.join(backend_dir, "reports"), exist_ok=True)
os.makedirs(os.path.join(backend_dir, "assets"), exist_ok=True)

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="EcoTrace - Campus Carbon Auditor API",
    description="Clean, beginner-friendly REST API for auditing college carbon footprint (UN SDG 13: Climate Action)",
    version="1.0"
)

# Serve static assets (such as the EcoTrace logo)
app.mount("/assets", StaticFiles(directory=os.path.join(backend_dir, "assets")), name="assets")

# Configure CORS so the React frontend can seamlessly communicate with this API during hackathon demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allows requests from any origin (e.g. http://localhost:3000, 5173)
    allow_credentials=True,
    allow_methods=["*"],       # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],       # Allows all headers
)

# Connect all feature routers under the '/api' prefix
app.include_router(bills_router, prefix="/api")
app.include_router(overview_router, prefix="/api")
app.include_router(whatif_router, prefix="/api")
app.include_router(leaderboard_router, prefix="/api")
app.include_router(mess_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(anomalies_router, prefix="/api")
app.include_router(tips_router, prefix="/api")


from fastapi.responses import FileResponse, HTMLResponse

# Path to the root frontend directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))



def _serve_page(filename: str):
    file_path = os.path.join(parent_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return HTMLResponse(f"<h1>EcoTrace {filename} not found</h1>", status_code=404)


@app.get("/app", response_class=HTMLResponse)
@app.get("/index.html")
def get_app():
    """Serves the EcoTrace frontend gateway (redirects to login or dashboard)."""
    return _serve_page("index.html")


@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html")
def get_login():
    """Serves the EcoTrace authentication page."""
    return _serve_page("login.html")


@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard.html")
def get_dashboard():
    """Serves the EcoTrace campus overview dashboard."""
    return _serve_page("dashboard.html")


@app.get("/scanner", response_class=HTMLResponse)
@app.get("/scanner.html")
def get_scanner():
    """Serves the EcoTrace MSEDCL bill OCR scanner page."""
    return _serve_page("scanner.html")


@app.get("/league", response_class=HTMLResponse)
@app.get("/league.html")
def get_league():
    """Serves the EcoTrace inter-department carbon league leaderboard."""
    return _serve_page("league.html")


@app.get("/mess", response_class=HTMLResponse)
@app.get("/mess.html")
def get_mess():
    """Serves the EcoTrace hostel mess & food carbon auditor."""
    return _serve_page("mess.html")


@app.get("/simulator", response_class=HTMLResponse)
@app.get("/simulator.html")
def get_simulator():
    """Serves the EcoTrace rooftop solar & operational savings simulator."""
    return _serve_page("simulator.html")


@app.get("/energy", response_class=HTMLResponse)
@app.get("/energy.html")
def get_energy():
    """Serves the EcoTrace departmental energy & anomaly detection page."""
    return _serve_page("energy.html")


@app.get("/reports", response_class=HTMLResponse)
@app.get("/reports.html")
def get_reports():
    """Serves the EcoTrace NAAC Criterion 7 & NIRF Institutional Green Audit Report."""
    return _serve_page("reports.html")


@app.get("/styles.css")
def get_styles():
    """Serves the frontend stylesheet."""
    css_file = os.path.join(parent_dir, "styles.css")
    return FileResponse(css_file, media_type="text/css")


@app.get("/app.js")
def get_script():
    """Serves the frontend application JavaScript."""
    js_file = os.path.join(parent_dir, "app.js")
    return FileResponse(js_file, media_type="application/javascript")


@app.get("/")
def root():
    """
    Health check and welcome endpoint.
    Points developers and judges to the dashboard and API documentation.
    """
    return {
        "app_name": "EcoTrace",
        "tagline": "Campus Carbon Footprint Auditor (UN SDG 13: Climate Action)",
        "dashboard_url": "http://localhost:8000/app",
        "docs_url": "http://localhost:8000/docs",
        "logo_url": "http://localhost:8000/assets/logo.png",
        "message": "EcoTrace API is running. Visit /app for the dashboard or /docs for API testing."
    }
