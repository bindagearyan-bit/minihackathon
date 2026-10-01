# supabase_seed.py - Seeds data directly into Supabase via the REST API using service_role key.
# Run after executing supabase_schema.sql in the Supabase SQL Editor.
# Run with: python supabase_seed.py

import os
import csv
from supabase import create_client

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kttqcugrqroesetwkieb.supabase.co")
SUPABASE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0dHFjdWdycXJvZXNldHdraWViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDgyNzYwNSwiZXhwIjoyMTA2NDAzNjA1fQ.sIgeADJzSmOd8tSJT8nwj2Q24lSnmxux20i9ZKBeXBQ"
)


def seed_supabase():
    """Seeds departments, historical usage, and mess meals into Supabase."""
    print("Connecting to Supabase at:", SUPABASE_URL)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 1. Read CSV and insert departments
    csv_file_path = os.path.join("data", "monthly_usage_history.csv")
    departments_cache = {}
    rows_data = []

    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            dept_name = row["department"].strip()
            students = int(row["students"])
            departments_cache[dept_name] = students
            rows_data.append(row)

    print("Inserting departments into Supabase...")
    for dept_name, students in departments_cache.items():
        try:
            supabase.table("departments").upsert(
                {"name": dept_name, "students": students},
                on_conflict="name"
            ).execute()
        except Exception as e:
            print(f"Error inserting department {dept_name}:", e)

    # Fetch inserted department IDs
    dept_res = supabase.table("departments").select("id, name").execute()
    dept_id_map = {d["name"]: d["id"] for d in dept_res.data}
    print(f"Added {len(dept_id_map)} departments into Supabase")

    # 2. Insert Monthly Usages
    print("Inserting monthly usage records into Supabase...")
    usage_payloads = []
    for row in rows_data:
        dept_name = row["department"].strip()
        dept_id = dept_id_map.get(dept_name)
        if dept_id:
            usage_payloads.append({
                "department_id": dept_id,
                "month": row["month"].strip(),
                "units_kwh": float(row["units_kwh"]),
                "amount_inr": float(row["amount_inr"]),
                "co2_kg": float(row["co2_kg"])
            })

    try:
        supabase.table("monthly_usages").insert(usage_payloads).execute()
        print(f"Added {len(usage_payloads)} usage rows into Supabase")
    except Exception as e:
        print("Error inserting monthly usage:", e)

    # 3. Insert Mess Meals
    print("Inserting weekly mess meals into Supabase...")
    mess_meals_data = [
        {"day": "Monday", "slot": "lunch", "meal_name": "Poha", "meal_type": "veg", "votes": 0},
        {"day": "Monday", "slot": "dinner", "meal_name": "Varan Bhaat", "meal_type": "veg", "votes": 0},
        {"day": "Tuesday", "slot": "lunch", "meal_name": "Misal Pav", "meal_type": "veg", "votes": 0},
        {"day": "Tuesday", "slot": "dinner", "meal_name": "Egg Curry", "meal_type": "egg", "votes": 0},
        {"day": "Wednesday", "slot": "lunch", "meal_name": "Pithla Bhakri", "meal_type": "veg", "votes": 0},
        {"day": "Wednesday", "slot": "dinner", "meal_name": "Chicken Rassa", "meal_type": "chicken", "votes": 0},
        {"day": "Thursday", "slot": "lunch", "meal_name": "Veg Pulao", "meal_type": "veg", "votes": 0},
        {"day": "Thursday", "slot": "dinner", "meal_name": "Dal Tadka with Rice", "meal_type": "veg", "votes": 0},
        {"day": "Friday", "slot": "lunch", "meal_name": "Usal Pav", "meal_type": "veg", "votes": 0},
        {"day": "Friday", "slot": "dinner", "meal_name": "Egg Bhurji", "meal_type": "egg", "votes": 0},
        {"day": "Saturday", "slot": "lunch", "meal_name": "Sabudana Khichdi", "meal_type": "veg", "votes": 0},
        {"day": "Saturday", "slot": "dinner", "meal_name": "Mutton Thali", "meal_type": "mutton", "votes": 0},
        {"day": "Sunday", "slot": "lunch", "meal_name": "Puri Bhaji", "meal_type": "veg", "votes": 0},
        {"day": "Sunday", "slot": "dinner", "meal_name": "Chicken Biryani", "meal_type": "chicken", "votes": 0}
    ]

    try:
        supabase.table("mess_meals").insert(mess_meals_data).execute()
        print(f"Added {len(mess_meals_data)} mess meals into Supabase")
    except Exception as e:
        print("Error inserting mess meals:", e)

    print("Supabase database successfully initialized and seeded!")


if __name__ == "__main__":
    seed_supabase()
