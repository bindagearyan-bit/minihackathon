# seed.py - Seeds the database with 6 months of historical campus usage data and weekly mess meals.
# Run with: python seed.py

import os
import csv
from database import engine, SessionLocal, Base
from models import Department, MonthlyUsage, MessMeal


def seed_database():
    """
    Cleans and populates the database with initial demo data.
    1. Recreates all database tables.
    2. Imports departments and 6 months of usage from data/monthly_usage_history.csv.
    3. Populates 14 weekly mess menu meals (lunch and dinner for 7 days).
    """
    print("Resetting database tables...")
    # Drop all existing tables to guarantee a clean state for the demo
    Base.metadata.drop_all(bind=engine)
    # Create all tables afresh
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Step 1: Read CSV and insert departments and monthly usage history
        csv_file_path = os.path.join("data", "monthly_usage_history.csv")

        departments_dict = {}
        usage_rows_count = 0

        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                dept_name = row["department"].strip()
                students_count = int(row["students"])

                # If department does not exist in our dictionary, create it
                if dept_name not in departments_dict:
                    new_dept = Department(
                        name=dept_name,
                        students=students_count
                    )
                    db.add(new_dept)
                    db.commit()
                    db.refresh(new_dept)
                    departments_dict[dept_name] = new_dept

                # Create MonthlyUsage record
                dept_obj = departments_dict[dept_name]
                usage_entry = MonthlyUsage(
                    department_id=dept_obj.id,
                    month=row["month"].strip(),
                    units_kwh=float(row["units_kwh"]),
                    amount_inr=float(row["amount_inr"]),
                    co2_kg=float(row["co2_kg"])
                )
                db.add(usage_entry)
                usage_rows_count += 1

        db.commit()
        print(f"Added {len(departments_dict)} departments")
        print(f"Added {usage_rows_count} usage rows")

        # Step 2: Add 14 Maharashtrian mess meals (Lunch and Dinner for 7 days)
        mess_meals_data = [
            {"day": "Monday", "slot": "lunch", "meal_name": "Poha", "meal_type": "veg"},
            {"day": "Monday", "slot": "dinner", "meal_name": "Varan Bhaat", "meal_type": "veg"},
            {"day": "Tuesday", "slot": "lunch", "meal_name": "Misal Pav", "meal_type": "veg"},
            {"day": "Tuesday", "slot": "dinner", "meal_name": "Egg Curry", "meal_type": "egg"},
            {"day": "Wednesday", "slot": "lunch", "meal_name": "Pithla Bhakri", "meal_type": "veg"},
            {"day": "Wednesday", "slot": "dinner", "meal_name": "Chicken Rassa", "meal_type": "chicken"},
            {"day": "Thursday", "slot": "lunch", "meal_name": "Veg Pulao", "meal_type": "veg"},
            {"day": "Thursday", "slot": "dinner", "meal_name": "Dal Tadka with Rice", "meal_type": "veg"},
            {"day": "Friday", "slot": "lunch", "meal_name": "Usal Pav", "meal_type": "veg"},
            {"day": "Friday", "slot": "dinner", "meal_name": "Egg Bhurji", "meal_type": "egg"},
            {"day": "Saturday", "slot": "lunch", "meal_name": "Sabudana Khichdi", "meal_type": "veg"},
            {"day": "Saturday", "slot": "dinner", "meal_name": "Mutton Thali", "meal_type": "mutton"},
            {"day": "Sunday", "slot": "lunch", "meal_name": "Puri Bhaji", "meal_type": "veg"},
            {"day": "Sunday", "slot": "dinner", "meal_name": "Chicken Biryani", "meal_type": "chicken"}
        ]

        for meal_item in mess_meals_data:
            meal = MessMeal(
                day=meal_item["day"],
                slot=meal_item["slot"],
                meal_name=meal_item["meal_name"],
                meal_type=meal_item["meal_type"],
                votes=0
            )
            db.add(meal)

        db.commit()
        print(f"Added {len(mess_meals_data)} meals")
        print("Database seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
