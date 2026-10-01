# routers/anomalies.py - Feature 8: Statistical anomaly alerts for unusual electricity spikes.

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import AnomalyResponse
from services.anomaly_service import detect_monthly_anomalies

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("", response_model=AnomalyResponse)
def get_anomalies(month: Optional[str] = "2026-10", db: Session = Depends(get_db)):
    """
    Scans departmental electricity consumption for statistical anomalies and energy spikes.
    Flags departments with consumption > 1.5 standard deviations (z-score) or > 30% above 3-month baseline.
    """
    anomalies = detect_monthly_anomalies(db, month)

    if anomalies:
        message = f"{len(anomalies)} unusual electricity usage alert(s) detected."
    else:
        message = "No unusual usage this month."

    return {
        "month": month,
        "anomalies": anomalies,
        "message": message
    }
