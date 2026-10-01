# whatif_service.py - Calculation logic for the What-If campus savings simulator.
# Computes energy, carbon, and financial savings for PC management, solar installation, and LED lighting.

from config import (
    GRID_FACTOR,
    TARIFF_INR_PER_KWH,
    SOLAR_UNITS_PER_KW_PER_DAY,
    SOLAR_COST_PER_KW_INR,
)
from services.carbon_service import calculate_co2, calculate_cost, format_inr


def calculate_pc_savings(
    lab_pcs: int,
    pc_watts: int,
    hours_saved_per_day: float,
    working_days_per_month: int
) -> dict:
    """
    Calculates monthly electricity, CO2, and money saved by turning off lab PCs earlier.
    Formula: kWh = PCs × Watts × hours saved × days ÷ 1000 W/kW
    """
    # Step 1: Calculate energy saved in Watt-hours, then divide by 1000 for kWh
    # Energy (kWh) = count × power (W) × hours × days ÷ 1000
    watt_hours = lab_pcs * pc_watts * hours_saved_per_day * working_days_per_month
    kwh = watt_hours / 1000.0

    # Step 2: Convert kWh to CO2 and Rupee savings
    co2 = calculate_co2(kwh)
    inr = calculate_cost(kwh)

    return {
        "name": "Switch off lab PCs earlier",
        "kwh_per_month": round(kwh, 1),
        "co2_kg_per_month": round(co2, 1),
        "inr_per_month": round(inr)
    }


def calculate_solar_savings(solar_kw: float) -> dict:
    """
    Calculates monthly generation from proposed rooftop solar installation.
    Formula: kWh = kW capacity × 4 units/day × 30 days
    """
    # Step 1: Rooftop solar generation in India (~4 units per kW per day)
    kwh = solar_kw * SOLAR_UNITS_PER_KW_PER_DAY * 30.0

    # Step 2: Calculate clean energy CO2 offset and bill reduction
    co2 = calculate_co2(kwh)
    inr = calculate_cost(kwh)

    return {
        "name": "Rooftop solar",
        "kwh_per_month": round(kwh, 1),
        "co2_kg_per_month": round(co2, 1),
        "inr_per_month": round(inr)
    }


def calculate_led_savings(
    led_tubes_replaced: int,
    led_hours_per_day: float
) -> dict:
    """
    Calculates savings by replacing old 40W fluorescent tubes with modern 18W LED tubes.
    Power saved per tube = 40W - 18W = 22 Watts
    Formula: kWh = tubes × 22W × hours × 30 days ÷ 1000 W/kW
    """
    # Step 1: Watts saved per tube replaced
    watts_saved_per_tube = 40 - 18  # 22 Watts saved per light fixture

    # Step 2: Total monthly energy saved in kWh
    watt_hours = led_tubes_replaced * watts_saved_per_tube * led_hours_per_day * 30.0
    kwh = watt_hours / 1000.0

    # Step 3: Convert to CO2 and Rupee savings
    co2 = calculate_co2(kwh)
    inr = calculate_cost(kwh)

    return {
        "name": "LED tubes",
        "kwh_per_month": round(kwh, 1),
        "co2_kg_per_month": round(co2, 1),
        "inr_per_month": round(inr)
    }


def simulate_whatif(data) -> dict:
    """
    Aggregates all selected energy efficiency interventions and calculates annual impact.
    Calculates rooftop solar payback duration in years.
    """
    # Run calculations for each of the 3 actions
    pc_result = calculate_pc_savings(
        data.lab_pcs,
        data.pc_watts,
        data.hours_saved_per_day,
        data.working_days_per_month
    )
    solar_result = calculate_solar_savings(data.solar_kw)
    led_result = calculate_led_savings(
        data.led_tubes_replaced,
        data.led_hours_per_day
    )

    actions = [pc_result, solar_result, led_result]

    # Calculate monthly totals
    total_kwh_per_month = 0.0
    total_co2_kg_per_month = 0.0
    total_inr_per_month = 0.0

    for action in actions:
        total_kwh_per_month += action["kwh_per_month"]
        total_co2_kg_per_month += action["co2_kg_per_month"]
        total_inr_per_month += action["inr_per_month"]

    # Calculate annual totals (12 months in a year)
    # 1 tonne = 1000 kg CO2
    total_co2_tonnes_per_year = round((total_co2_kg_per_month * 12.0) / 1000.0, 1)
    total_inr_per_year = round(total_inr_per_month * 12.0)

    # Calculate solar payback period: Capital Cost ÷ Annual Savings
    solar_payback_years = 0.0
    if data.solar_kw > 0:
        solar_capital_cost = data.solar_kw * SOLAR_COST_PER_KW_INR
        annual_solar_savings_inr = solar_result["inr_per_month"] * 12.0
        if annual_solar_savings_inr > 0:
            solar_payback_years = round(solar_capital_cost / annual_solar_savings_inr, 1)

    # Format human-readable summary
    formatted_money = format_inr(total_inr_per_year)
    summary = f"These changes can save {formatted_money} and {total_co2_tonnes_per_year} tonnes of CO2 every year."

    return {
        "actions": actions,
        "total_kwh_per_month": round(total_kwh_per_month, 1),
        "total_co2_kg_per_month": round(total_co2_kg_per_month, 1),
        "total_inr_per_month": round(total_inr_per_month),
        "total_co2_tonnes_per_year": total_co2_tonnes_per_year,
        "total_inr_per_year": total_inr_per_year,
        "solar_payback_years": solar_payback_years,
        "summary": summary
    }
