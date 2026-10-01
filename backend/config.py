# config.py - All constants, emission factors, and thresholds used in the application.

# Central Electricity Authority (CEA) CO2 Baseline Database for the Indian Power Sector (Govt. of India)
# 1 unit (1 kWh) of electricity from the Indian grid emits approximately 0.71 kg of CO2
GRID_FACTOR = 0.71

# Average commercial / educational electricity tariff in Maharashtra/India in Rupees (₹) per kWh
TARIFF_INR_PER_KWH = 11.5

# Food carbon footprint factors (kg CO2 equivalent per meal plate)
# Source: Poore & Nemecek (2018), Science - "Reducing food's environmental impacts through producers and consumers"
FOOD_FACTORS = {
    "veg": 0.8,       # Vegetarian meal emits the lowest CO2 (0.8 kg)
    "egg": 1.3,       # Egg meal emits moderate CO2 (1.3 kg)
    "chicken": 2.5,   # Poultry meat emits high CO2 (2.5 kg)
    "mutton": 6.0     # Red meat emits the highest CO2 (6.0 kg)
}

# Display labels for each food type
FOOD_LABELS = {
    "veg": "Low",
    "egg": "Medium",
    "chicken": "High",
    "mutton": "Very High"
}

# Frontend color coding for each food type
FOOD_COLORS = {
    "veg": "green",
    "egg": "yellow",
    "chicken": "red",
    "mutton": "red"
}

# Total number of students dining in the college mess daily
MESS_STUDENTS = 900

# Rooftop solar power generation in India: on average 1 kW capacity generates 4 units (kWh) per sunny day
SOLAR_UNITS_PER_KW_PER_DAY = 4

# Approximate rooftop solar installation cost in Rupees (₹) per kW capacity
SOLAR_COST_PER_KW_INR = 50000

# Anomaly detection: flag if usage is 1.5 standard deviations above 3-month average (z-score)
ANOMALY_Z_THRESHOLD = 1.5

# Anomaly detection: flag if electricity usage jumps by more than 30% compared to 3-month average
ANOMALY_PERCENT_THRESHOLD = 30

# Peak solar power generation window when electricity from the grid is cleanest
SOLAR_HOURS = "11 AM to 3 PM"
