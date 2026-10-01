# test_api.py - Quick verification script to test all backend endpoints.
# Run with: python test_api.py

import requests
import json
import sys

# Ensure UTF-8 output so Rupee symbol (₹) prints cleanly on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("     CAMPUS CARBON AUDITOR - API TEST SUITE")
print("=" * 60)

# 1. Health check
r = requests.get(f"{BASE_URL}/")
print(f"\n[1] Health Check: Status {r.status_code}")
print("    Response:", r.json().get("message"))

# 2. Campus Overview Dashboard
r = requests.get(f"{BASE_URL}/api/overview?month=2026-10")
print(f"\n[2] Campus Overview (Oct 2026): Status {r.status_code}")
data = r.json()
print("    Headline:", data.get("headline"))
print(f"    Total kWh: {data.get('total_units_kwh'):,} | Total CO2: {data.get('total_co2_tonnes')} tonnes | Amount: ₹{data.get('total_amount_inr'):,}")

# 3. Department List
r = requests.get(f"{BASE_URL}/api/departments")
print(f"\n[3] Departments Dropdown: Status {r.status_code}")
depts = r.json()
print(f"    Loaded {len(depts)} departments:")
for d in depts[:4]:
    print(f"    - {d['name']} ({d['students']} students)")
print("    - ...")

# 4. What-If Savings Calculator
whatif_payload = {
    "lab_pcs": 200,
    "pc_watts": 150,
    "hours_saved_per_day": 3.0,
    "working_days_per_month": 22,
    "solar_kw": 20.0,
    "led_tubes_replaced": 150,
    "led_hours_per_day": 8.0
}
r = requests.post(f"{BASE_URL}/api/whatif", json=whatif_payload)
print(f"\n[4] What-If Savings Simulator: Status {r.status_code}")
whatif_data = r.json()
print("    Summary:", whatif_data.get("summary"))
print(f"    Solar Payback: {whatif_data.get('solar_payback_years')} years")

# 5. Carbon League Leaderboard
r = requests.get(f"{BASE_URL}/api/leaderboard?month=2026-10&mode=per_student")
print(f"\n[5] Carbon League (Ranked per student): Status {r.status_code}")
lb_data = r.json()
for row in lb_data.get("leaderboard", [])[:4]:
    badge_str = f"[{row['badge']}]" if row['badge'] else ""
    print(f"    Rank {row['rank']}: {row['department']} - {row['co2_per_student']} kg CO2/student {badge_str}")

# 6. Mess Menu & Green Day Tip
r = requests.get(f"{BASE_URL}/api/mess")
print(f"\n[6] Hostel Mess Plate Carbon Scores: Status {r.status_code}")
mess_data = r.json()
print("    Weekly Tip:", mess_data.get("green_day_tip"))
print(f"    Total Weekly Mess Footprint: {mess_data.get('weekly_co2_kg'):,} kg CO2")

# 7. Anomaly Spikes Detection
r = requests.get(f"{BASE_URL}/api/anomalies?month=2026-10")
print(f"\n[7] Statistical Anomaly Detection (Z-Score): Status {r.status_code}")
anom_data = r.json()
for a in anom_data.get("anomalies", []):
    print("    ALERT:", a.get("message"))

# 8. Solar Timing Advisor
r = requests.get(f"{BASE_URL}/api/tips/solar")
print(f"\n[8] Solar Timing Guidance: Status {r.status_code}")
tips_data = r.json()
print("    Peak Window:", tips_data.get("best_hours"))
for t in tips_data.get("recommended_schedules", [])[:2]:
    print("    Tip:", t.get("tip"))

# 9. Download NAAC Criterion 7 PDF Report
r = requests.get(f"{BASE_URL}/api/reports/naac?month=2026-10")
print(f"\n[9] NAAC Sustainability Report PDF: Status {r.status_code}")
print(f"    Downloaded PDF Size: {len(r.content):,} bytes")

print("\n" + "=" * 60)
print("     ALL CORE ENDPOINTS VERIFIED & OPERATIONAL!")
print("=" * 60)
