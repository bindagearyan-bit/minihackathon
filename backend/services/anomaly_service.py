# anomaly_service.py - Detects unusual electricity usage spikes across campus departments
# using statistical z-scores and percentage thresholds.

import statistics
from sqlalchemy.orm import Session

from config import (
    GRID_FACTOR,
    TARIFF_INR_PER_KWH,
    ANOMALY_Z_THRESHOLD,
    ANOMALY_PERCENT_THRESHOLD
)
from models import Department, MonthlyUsage
from services.carbon_service import format_inr


def detect_monthly_anomalies(db: Session, target_month: str) -> list:
    """
    Detects abnormal electricity consumption for departments in a given month.
    Compares the current month's usage to the 3 preceding months using mean, standard deviation, and z-score.
    Inputs: db (SQLAlchemy Session), target_month (str, format 'YYYY-MM')
    Output: list of anomaly dictionaries
    """
    anomalies = []

    # Retrieve all departments from database
    departments = db.query(Department).all()

    for dept in departments:
        # Step 1: Find the usage for the target month
        current_record = db.query(MonthlyUsage).filter(
            MonthlyUsage.department_id == dept.id,
            MonthlyUsage.month == target_month
        ).first()

        if not current_record:
            continue

        this_month_kwh = current_record.units_kwh

        # Step 2: Fetch the 3 preceding months for baseline comparison
        # Filter for months strictly prior to target_month, ordered most recent first
        prior_records = db.query(MonthlyUsage).filter(
            MonthlyUsage.department_id == dept.id,
            MonthlyUsage.month < target_month
        ).order_by(MonthlyUsage.month.desc()).limit(3).all()

        # If less than 2 previous months exist, we cannot calculate meaningful statistics
        if len(prior_records) < 2:
            continue

        last_3 = []
        for r in prior_records:
            last_3.append(r.units_kwh)

        # Step 3: Calculate the 3-month baseline mean and population standard deviation
        average_kwh = statistics.mean(last_3)

        if len(last_3) >= 2:
            spread = statistics.pstdev(last_3)
        else:
            spread = 0.0

        # Step 4: Calculate the z-score (number of standard deviations above average)
        # Avoid division by zero if all previous months had identical usage
        if spread > 0:
            z_score = (this_month_kwh - average_kwh) / spread
        else:
            z_score = 0.0

        # Step 5: Calculate percentage increase over average
        # Formula: ((current - average) / average) * 100
        if average_kwh > 0:
            percent_change = ((this_month_kwh - average_kwh) / average_kwh) * 100.0
        else:
            percent_change = 0.0

        # Step 6: Flag as anomaly if z-score > 1.5 OR percent increase > 30%
        is_anomaly = (z_score > ANOMALY_Z_THRESHOLD) or (percent_change > ANOMALY_PERCENT_THRESHOLD)

        if is_anomaly:
            # Step 7: Calculate extra units, extra CO2, and extra Rupee cost
            extra_kwh = max(0.0, this_month_kwh - average_kwh)
            extra_co2_kg = extra_kwh * GRID_FACTOR
            extra_inr = extra_kwh * TARIFF_INR_PER_KWH

            # High severity if jump is over 40%, otherwise medium
            if percent_change > 40.0:
                severity = "high"
            else:
                severity = "medium"

            # Formulate user-friendly alert message
            formatted_cost = format_inr(extra_inr)
            message = (
                f"{dept.name} used {round(percent_change, 1)}% more electricity than its 3-month average "
                f"(extra {formatted_cost} and {int(round(extra_co2_kg))} kg CO2)."
            )

            anomalies.append({
                "department": dept.name,
                "this_month_kwh": round(this_month_kwh),
                "average_kwh": round(average_kwh),
                "percent_change": round(percent_change, 1),
                "z_score": round(z_score, 1),
                "extra_co2_kg": round(extra_co2_kg, 1),
                "extra_inr": round(extra_inr),
                "severity": severity,
                "message": message
            })

    return anomalies
