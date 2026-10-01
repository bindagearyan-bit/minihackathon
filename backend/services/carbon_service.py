# carbon_service.py - Calculation logic for CO2 emissions and Indian Rupee conversions.
# Implements official CEA emission factor and Indian currency formatting.

from config import GRID_FACTOR, TARIFF_INR_PER_KWH


def calculate_co2(units_kwh: float) -> float:
    """
    Calculates CO2 emissions in kilograms from electricity units (kWh).
    Formula: CO2 (kg) = units used (kWh) × grid emission factor (0.71 kg/kWh)
    Input: units_kwh (float)
    Output: co2_kg rounded to 1 decimal place
    """
    # Step 1: Multiply units by CEA baseline factor (0.71 kg CO2 / kWh)
    co2_kg = units_kwh * GRID_FACTOR

    # Step 2: Return rounded to 1 decimal place as required
    return round(co2_kg, 1)


def calculate_cost(units_kwh: float) -> float:
    """
    Calculates estimated electricity cost in Indian Rupees (₹).
    Formula: Cost (₹) = units used (kWh) × tariff per unit (₹11.5)
    Input: units_kwh (float)
    Output: amount_inr rounded to whole rupee
    """
    # Step 1: Multiply units by tariff rate per kWh
    amount_inr = units_kwh * TARIFF_INR_PER_KWH

    # Step 2: Return rounded to whole rupees
    return round(amount_inr)


def format_inr(amount: float) -> str:
    """
    Formats a numeric amount into Indian currency format with ₹ sign.
    Example: 601910 becomes '₹6,01,910'.
    Input: amount (float or int)
    Output: formatted string
    """
    # Convert to rounded integer
    integer_value = int(round(amount))
    sign = "-" if integer_value < 0 else ""
    digits = str(abs(integer_value))

    # If 3 or fewer digits, no commas needed
    if len(digits) <= 3:
        return f"{sign}₹{digits}"

    # In Indian numbering, the last 3 digits represent hundreds (e.g., '910')
    last_three = digits[-3:]
    remaining = digits[:-3]

    # Group all preceding digits in pairs of two from right to left (thousands, lakhs, crores)
    pairs = []
    while len(remaining) > 2:
        pairs.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        pairs.insert(0, remaining)

    # Combine pairs and append the last three digits
    formatted = ",".join(pairs) + "," + last_three
    return f"{sign}₹{formatted}"
