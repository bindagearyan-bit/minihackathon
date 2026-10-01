# routers/mess.py - Feature 6: Mess plate carbon score and weekly Green Day pledge voting.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import MessMeal
from config import FOOD_FACTORS, FOOD_LABELS, FOOD_COLORS, MESS_STUDENTS

router = APIRouter(prefix="/mess", tags=["Mess"])

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@router.get("")
def get_mess_menu(db: Session = Depends(get_db)):
    """
    Returns the weekly mess menu with carbon scores, labels, and Green Day carbon saving tips.
    Groups meals from Monday to Sunday.
    """
    meals = db.query(MessMeal).all()

    # Step 1: Group meals by day of week
    grouped_days = {}
    for day_name in DAY_ORDER:
        grouped_days[day_name] = []

    weekly_co2_kg = 0.0
    highest_carbon_meal = None
    highest_carbon_factor = 0.0

    for meal in meals:
        # Determine carbon factor per plate from scientific benchmarks
        factor = FOOD_FACTORS.get(meal.meal_type.lower(), 0.8)
        label = FOOD_LABELS.get(meal.meal_type.lower(), "Low")
        color = FOOD_COLORS.get(meal.meal_type.lower(), "green")

        # Step 2: Add to total weekly footprint (meal factor × dining students)
        weekly_co2_kg += factor * MESS_STUDENTS

        # Track the meal with the highest carbon footprint for Green Day replacement tip
        if factor > highest_carbon_factor:
            highest_carbon_factor = factor
            highest_carbon_meal = meal

        meal_data = {
            "id": meal.id,
            "day": meal.day,
            "slot": meal.slot,
            "meal_name": meal.meal_name,
            "meal_type": meal.meal_type,
            "co2_per_plate": factor,
            "label": label,
            "color": color,
            "votes": meal.votes
        }

        if meal.day in grouped_days:
            grouped_days[meal.day].append(meal_data)

    # Step 3: Compute Green Day suggestion
    # Calculate savings if highest-carbon meal is replaced with vegetarian alternative (0.8 kg)
    veg_factor = FOOD_FACTORS["veg"]
    green_day_tip = "Hostel mess is running cleanly."

    if highest_carbon_meal and highest_carbon_factor > veg_factor:
        # Formula: (highest_factor - veg_factor) × student count
        saving_kg = (highest_carbon_factor - veg_factor) * MESS_STUDENTS
        green_day_tip = (
            f"Replacing {highest_carbon_meal.day} {highest_carbon_meal.slot} "
            f"({highest_carbon_meal.meal_name}) with a veg thali saves "
            f"{int(round(saving_kg)):,} kg CO2 per week."
        )

    return {
        "days": grouped_days,
        "weekly_co2_kg": round(weekly_co2_kg, 1),
        "green_day_tip": green_day_tip
    }


@router.post("/{meal_id}/vote")
def vote_meal(meal_id: int, db: Session = Depends(get_db)):
    """
    Increments student vote count for a meal pledge ('I would eat this on Green Day').
    """
    meal = db.query(MessMeal).filter(MessMeal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    # Increment vote counter
    meal.votes += 1
    db.commit()
    db.refresh(meal)

    factor = FOOD_FACTORS.get(meal.meal_type.lower(), 0.8)
    label = FOOD_LABELS.get(meal.meal_type.lower(), "Low")
    color = FOOD_COLORS.get(meal.meal_type.lower(), "green")

    return {
        "id": meal.id,
        "day": meal.day,
        "slot": meal.slot,
        "meal_name": meal.meal_name,
        "meal_type": meal.meal_type,
        "co2_per_plate": factor,
        "label": label,
        "color": color,
        "votes": meal.votes,
        "message": f"Vote recorded for {meal.meal_name}!"
    }
