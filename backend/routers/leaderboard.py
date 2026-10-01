# routers/leaderboard.py - Feature 5: Carbon League fair department leaderboard.
# Ranks departments by carbon intensity (per student or total) with badges and trend indicators.

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Department, MonthlyUsage

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("")
def get_leaderboard(
    month: Optional[str] = "2026-10",
    mode: Optional[str] = "per_student",
    db: Session = Depends(get_db)
):
    """
    Ranks campus departments in the Carbon League for a given month.
    Sorts from lowest CO2 (Rank 1, best) to highest.
    Provides fair per-student normalization, badges, trends, and Rupee expenditures.
    """
    # Step 1: Find previous month for comparison
    all_months = db.query(MonthlyUsage.month).filter(
        MonthlyUsage.month <= month
    ).distinct().order_by(MonthlyUsage.month.desc()).all()
    months_list = [m[0] for m in all_months]
    prev_month = months_list[1] if len(months_list) > 1 else None

    # Step 2: Gather data for each department
    departments = db.query(Department).all()
    rows = []

    for dept in departments:
        # Current month usage
        current = db.query(MonthlyUsage).filter(
            MonthlyUsage.department_id == dept.id,
            MonthlyUsage.month == month
        ).first()

        if not current:
            continue

        co2_kg = current.co2_kg
        students = dept.students if dept.students > 0 else 1

        # Step 3: Compute CO2 per student step by step
        # CO2 per student (kg) = total CO2 (kg) ÷ number of students
        co2_per_student = round(co2_kg / students, 2)

        # Step 4: Compare with previous month
        prev = None
        if prev_month:
            prev = db.query(MonthlyUsage).filter(
                MonthlyUsage.department_id == dept.id,
                MonthlyUsage.month == prev_month
            ).first()

        prev_co2_kg = prev.co2_kg if prev else co2_kg
        prev_per_student = round(prev_co2_kg / students, 2)

        if prev_co2_kg > 0:
            change_percent = round(((co2_kg - prev_co2_kg) / prev_co2_kg) * 100.0, 1)
        else:
            change_percent = 0.0

        # Step 5: Determine trend indicator
        if change_percent > 0.5:
            trend = "up"
        elif change_percent < -0.5:
            trend = "down"
        else:
            trend = "same"

        rows.append({
            "department_id": dept.id,
            "department": dept.name,
            "students": students,
            "units_kwh": round(current.units_kwh),
            "co2_kg": round(co2_kg, 1),
            "co2_per_student": co2_per_student,
            "previous_co2_kg": round(prev_co2_kg, 1),
            "previous_per_student": prev_per_student,
            "change_percent": change_percent,
            "trend": trend,
            "amount_inr": round(current.amount_inr)
        })

    # Step 6: Sort rows (lowest CO2 = rank 1 = best)
    if mode == "total":
        rows.sort(key=lambda item: item["co2_kg"])
    else:
        # Default to per_student ranking
        rows.sort(key=lambda item: item["co2_per_student"])

    # Step 7: Identify the department with the biggest drop (most negative change_percent)
    most_improved_id = None
    best_drop = 0.0
    for r in rows:
        if r["change_percent"] < best_drop:
            best_drop = r["change_percent"]
            most_improved_id = r["department_id"]

    # Step 8: Assign ranks, badges, and color codes
    total_depts = len(rows)
    for index, item in enumerate(rows):
        rank = index + 1
        item["rank"] = rank

        # Badges logic
        if rank == 1:
            item["badge"] = "Green Champion"
        elif item["department_id"] == most_improved_id:
            item["badge"] = "Most Improved"
        elif item["change_percent"] > 10.0:
            item["badge"] = "Needs Attention"
        else:
            item["badge"] = ""

        # Color coding for frontend UI
        if rank <= 3:
            item["color"] = "green"    # Top 3 performers
        elif rank > (total_depts - 2):
            item["color"] = "red"      # Bottom 2 performers
        else:
            item["color"] = "yellow"   # Mid-tier performers

    explanation = "Ranked by CO2 per student so that big departments are not treated unfairly."

    return {
        "month": month,
        "mode": mode,
        "explanation": explanation,
        "leaderboard": rows
    }
