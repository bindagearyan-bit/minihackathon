# routers/reports.py - Feature 7: One-click NAAC Criterion 7 / NIRF Sustainability PDF report generator.

import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models import MonthlyUsage
from services.report_service import generate_naac_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/naac")
def download_naac_report(month: Optional[str] = "2026-10", db: Session = Depends(get_db)):
    """
    Generates and downloads the official NAAC Criterion 7 / NIRF Green Campus Sustainability Report in PDF format.
    Includes executive summary, departmental breakdowns, six-month historical trends, and audit sources.
    """
    # Verify that usage data exists for the selected month
    records_count = db.query(MonthlyUsage).filter(MonthlyUsage.month == month).count()
    if records_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No usage data found for month '{month}' to generate report."
        )

    # Prepare output PDF path
    output_filename = f"Green_Campus_Report_{month}.pdf"
    output_path = os.path.join("reports", output_filename)

    # Generate PDF via ReportLab service
    generate_naac_pdf(db, month, output_path)

    # Return as downloadable file
    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type="application/pdf"
    )
