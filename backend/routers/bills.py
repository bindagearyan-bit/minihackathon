# routers/bills.py - API endpoints for scanning electricity bills with OCR and confirming saved bills.

import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import Department, Bill
from schemas import BillConfirm, BillOut, BillScanResponse
from services.carbon_service import calculate_co2, format_inr
from services.ocr_service import save_uploaded_file, scan_bill_pipeline

router = APIRouter(prefix="/bills", tags=["Bills"])


@router.post("/scan", response_model=BillScanResponse)
def scan_bill(file: UploadFile = File(...)):
    """
    Uploads an electricity bill (PNG, JPG, or PDF) and extracts consumption details using multilingual OCR.
    Does NOT save to database yet; allows user to review and correct extracted values.
    """
    # Step 1: Validate file extension
    filename = file.filename or ""
    allowed_extensions = [".png", ".jpg", ".jpeg", ".pdf"]
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PNG, JPG or PDF bill"
        )

    # Step 2: Save the uploaded bill to uploads/ folder
    saved_filename = save_uploaded_file(file, "uploads")
    file_path = os.path.join("uploads", saved_filename)

    # Step 3: Run OCR pipeline to extract units, amount, and billing month
    scan_result = scan_bill_pipeline(file_path, saved_filename)

    return scan_result


@router.post("/confirm", response_model=BillOut)
def confirm_bill(bill_in: BillConfirm, db: Session = Depends(get_db)):
    """
    Confirms and permanently stores an electricity bill in the database.
    Allows user-corrected numbers before computing the final CO2 footprint.
    """
    # Step 1: Verify department exists
    department = db.query(Department).filter(Department.id == bill_in.department_id).first()
    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    # Step 2: Calculate official CO2 footprint using CEA grid emission factor
    co2_kg = calculate_co2(bill_in.units_kwh)

    # Step 3: Create and save the Bill database record
    new_bill = Bill(
        department_id=bill_in.department_id,
        bill_month=bill_in.bill_month,
        units_kwh=bill_in.units_kwh,
        amount_inr=bill_in.amount_inr,
        co2_kg=co2_kg,
        file_name=bill_in.file_name,
        raw_text=bill_in.raw_text
    )
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    # Step 4: Format summary showing both CO2 and ₹ (Feature 3)
    formatted_inr = format_inr(bill_in.amount_inr)
    formatted_co2 = f"{int(round(co2_kg)):,}"
    summary = f"This bill = {formatted_co2} kg CO2 and {formatted_inr}"

    return {
        "id": new_bill.id,
        "department": department.name,
        "units_kwh": new_bill.units_kwh,
        "co2_kg": new_bill.co2_kg,
        "amount_inr": new_bill.amount_inr,
        "summary": summary
    }


@router.get("", response_model=list)
def get_bills(db: Session = Depends(get_db)):
    """
    Returns the list of all saved electricity bills, newest first, showing CO2 and ₹ values.
    """
    bills = db.query(Bill).order_by(Bill.id.desc()).all()
    results = []

    for b in bills:
        results.append({
            "id": b.id,
            "department": b.department.name if b.department else "Unknown",
            "bill_month": b.bill_month,
            "units_kwh": b.units_kwh,
            "co2_kg": b.co2_kg,
            "amount_inr": b.amount_inr,
            "file_name": b.file_name,
            "created_at": b.created_at.strftime("%Y-%m-%d %H:%M") if b.created_at else ""
        })

    return results
