# routers/tips.py - Feature 9: Solar timing optimization tips for heavy campus electrical loads.

from fastapi import APIRouter
from config import SOLAR_HOURS
from services.carbon_service import calculate_co2, calculate_cost, format_inr

router = APIRouter(prefix="/tips", tags=["Tips"])


@router.get("/solar")
def get_solar_tips():
    """
    Suggests scheduling heavy campus loads during peak solar window (11 AM to 3 PM)
    to leverage cleaner grid power and self-generated rooftop solar.
    """
    # Typical heavy electrical loads across an Indian engineering campus
    heavy_loads = [
        {"name": "Water pump", "kw": 7.5, "hours_per_day": 3.0},
        {"name": "Lab server room", "kw": 5.0, "hours_per_day": 6.0},
        {"name": "Hostel laundry", "kw": 4.0, "hours_per_day": 4.0},
        {"name": "Workshop machines", "kw": 15.0, "hours_per_day": 3.0}
    ]

    tips = []
    for load in heavy_loads:
        # Formula: monthly kWh = power (kW) × daily hours × 30 days
        monthly_kwh = load["kw"] * load["hours_per_day"] * 30.0
        monthly_co2 = calculate_co2(monthly_kwh)
        monthly_inr = calculate_cost(monthly_kwh)

        tips.append({
            "name": load["name"],
            "power_kw": load["kw"],
            "hours_per_day": load["hours_per_day"],
            "monthly_kwh": round(monthly_kwh),
            "monthly_co2_kg": round(monthly_co2, 1),
            "monthly_inr": round(monthly_inr),
            "monthly_cost_formatted": format_inr(monthly_inr),
            "tip": f"Run the {load['name']} between {SOLAR_HOURS}, when the grid has the most solar power."
        })

    explanation = (
        f"Between {SOLAR_HOURS}, solar power is highest, so the electricity you use at that time comes from cleaner sources. "
        "If the campus adds rooftop solar, these hours use your own free electricity."
    )

    return {
        "best_hours": SOLAR_HOURS,
        "explanation": explanation,
        "recommended_schedules": tips
    }
