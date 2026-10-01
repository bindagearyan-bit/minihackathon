# routers/overview.py - Campus dashboard overview metrics, department breakdown, and trend chart data.

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Department, MonthlyUsage
from schemas import DepartmentOut
from services.carbon_service import format_inr

router = APIRouter(tags=["Overview"])


@router.get("/overview")
def get_campus_overview(month: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns campus-wide electricity consumption, CO2 footprint in tonnes,
    Rupee expenditure, previous month comparison, department list, and 6-month trend.
    """
    # Step 1: If month is not provided, pick the latest month available in the database
    if not month:
        latest_record = db.query(MonthlyUsage).order_by(MonthlyUsage.month.desc()).first()
        if latest_record:
            month = latest_record.month
        else:
            month = "2026-10"

    # Step 2: Query records for the target month
    current_records = db.query(MonthlyUsage).filter(MonthlyUsage.month == month).all()

    total_units_kwh = sum([r.units_kwh for r in current_records])
    total_co2_kg = sum([r.co2_kg for r in current_records])
    total_co2_tonnes = round(total_co2_kg / 1000.0, 1)
    total_amount_inr = sum([r.amount_inr for r in current_records])

    # Step 3: Find previous month and calculate change percentage
    all_distinct_months = db.query(MonthlyUsage.month).filter(
        MonthlyUsage.month <= month
    ).distinct().order_by(MonthlyUsage.month.desc()).all()

    sorted_months = [m[0] for m in all_distinct_months]
    change_percent = 0.0

    if len(sorted_months) > 1:
        prev_month = sorted_months[1]
        prev_records = db.query(MonthlyUsage).filter(MonthlyUsage.month == prev_month).all()
        prev_total_kwh = sum([r.units_kwh for r in prev_records])
        if prev_total_kwh > 0:
            change_percent = round(((total_units_kwh - prev_total_kwh) / prev_total_kwh) * 100.0, 1)

    # Step 4: Department-wise breakdown
    by_department = []
    for r in current_records:
        dept_name = r.department.name if r.department else "Unknown"
        by_department.append({
            "department": dept_name,
            "units_kwh": round(r.units_kwh),
            "co2_kg": round(r.co2_kg, 1),
            "amount_inr": round(r.amount_inr)
        })

    # Step 5: Six-month trend data for historical charts (chronological order)
    trend = []
    trend_months = list(reversed(sorted_months[:6]))
    for m in trend_months:
        m_records = db.query(MonthlyUsage).filter(MonthlyUsage.month == m).all()
        m_co2 = sum([x.co2_kg for x in m_records])
        m_inr = sum([x.amount_inr for x in m_records])
        trend.append({
            "month": m,
            "co2_kg": round(m_co2, 1),
            "amount_inr": round(m_inr)
        })

    # Step 6: Plain-English headline (Feature 3: CO2 always with ₹)
    formatted_kwh = f"{int(round(total_units_kwh)):,}"
    formatted_money = format_inr(total_amount_inr)
    headline = (
        f"This month the campus used {formatted_kwh} kWh, "
        f"which is {total_co2_tonnes} tonnes of CO2 and {formatted_money}."
    )

    return {
        "month": month,
        "total_units_kwh": round(total_units_kwh),
        "total_co2_kg": round(total_co2_kg, 1),
        "total_co2_tonnes": total_co2_tonnes,
        "total_amount_inr": round(total_amount_inr),
        "change_percent": change_percent,
        "by_department": by_department,
        "trend": trend,
        "headline": headline
    }


@router.get("/departments", response_model=list[DepartmentOut])
def get_departments(db: Session = Depends(get_db)):
    """
    Returns the list of campus departments for frontend dropdown selectors.
    """
    departments = db.query(Department).order_by(Department.id).all()
    return departments
