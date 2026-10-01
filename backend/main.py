# main.py - Main entry point for the Campus Carbon Auditor backend application.
# Configures FastAPI, CORS for React frontend integration, database tables, and registers all routers.

import os
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
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("assets", exist_ok=True)

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="EcoTrace - Campus Carbon Auditor API",
    description="Clean, beginner-friendly REST API for auditing college carbon footprint (UN SDG 13: Climate Action)",
    version="1.0"
)

# Serve static assets (such as the EcoTrace logo)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

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


@app.get("/")
def root():
    """
    Health check and welcome endpoint.
    Points developers and judges to the interactive Swagger API documentation.
    """
    return {
        "app_name": "EcoTrace",
        "tagline": "Campus Carbon Footprint Auditor (UN SDG 13: Climate Action)",
        "logo_url": "/assets/logo.png",
        "message": "EcoTrace API is running. Visit /docs to test all APIs."
    }
