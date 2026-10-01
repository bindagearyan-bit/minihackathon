# schemas.py - Defines Pydantic schemas for data validation and API documentation.
# Ensures all inputs and outputs conform to expected types with clear validation rules.

from typing import Optional, List
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Department Schemas
# ---------------------------------------------------------
class DepartmentOut(BaseModel):
    """Schema returned for department list in dropdowns."""
    id: int = Field(description="Unique ID of the department", example=1)
    name: str = Field(description="Department name", example="Computer")
    students: int = Field(description="Number of students in department", example=480)

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# Bill Schemas
# ---------------------------------------------------------
class BillScanResponse(BaseModel):
    """Schema returned right after OCR scans a bill."""
    units_kwh: Optional[float] = Field(None, description="Units consumed (kWh) extracted from bill", example=3076.0)
    units_confidence: str = Field(description="Confidence level for units: high or low", example="high")
    amount_inr: Optional[float] = Field(None, description="Total amount in ₹ extracted from bill", example=38459.0)
    amount_confidence: str = Field(description="Confidence level for amount: high or low", example="high")
    bill_month: Optional[str] = Field(None, description="Billing month extracted from bill", example="September 2026")
    month_confidence: str = Field(description="Confidence level for month: high or low", example="high")
    co2_kg: Optional[float] = Field(None, description="Calculated preview carbon footprint in kg CO2", example=2184.0)
    formula: str = Field(description="Step-by-step formula explanation", example="3076 kWh × 0.71 kg/kWh (CEA India grid factor)")
    file_name: str = Field(description="Saved file name in uploads directory", example="1696145000_bill.png")
    raw_text: str = Field(description="Raw text detected by OCR", example="MSEDCL Electricity Bill...")
    message: str = Field(description="Status message for user", example="Bill read successfully. Please check the values before saving.")


class BillConfirm(BaseModel):
    """Schema sent by user to confirm and save a bill after reviewing OCR values."""
    department_id: int = Field(..., description="ID of department to assign bill to", example=1)
    bill_month: str = Field(..., description="Billing month (e.g., 'September 2026')", example="September 2026")
    units_kwh: float = Field(..., gt=0, description="Electricity consumed in kWh (must be greater than 0)", example=3076.0)
    amount_inr: float = Field(..., ge=0, description="Total bill amount in ₹ (must be 0 or more)", example=38459.0)
    file_name: str = Field(..., description="File name returned from scan step", example="1696145000_bill.png")
    raw_text: Optional[str] = Field(None, description="Raw OCR text extracted from bill")


class BillOut(BaseModel):
    """Schema returned after a bill is confirmed and saved."""
    id: int = Field(description="Database ID of the saved bill", example=1)
    department: str = Field(description="Name of the assigned department", example="Computer")
    units_kwh: float = Field(description="Electricity units in kWh", example=3076.0)
    co2_kg: float = Field(description="Calculated CO2 footprint in kg", example=2184.0)
    amount_inr: float = Field(description="Total amount in ₹", example=38459.0)
    summary: str = Field(description="Readable summary showing both CO2 and ₹", example="This bill = 2,184 kg CO2 and ₹38,459")


class SavedBillItem(BaseModel):
    """Schema for individual saved bills in the list view."""
    id: int
    department: str
    bill_month: str
    units_kwh: float
    co2_kg: float
    amount_inr: float
    file_name: str
    created_at: str


# ---------------------------------------------------------
# What-If Simulator Schemas
# ---------------------------------------------------------
class WhatIfInput(BaseModel):
    """Input parameters for the What-If savings calculator."""
    lab_pcs: int = Field(default=200, ge=0, description="Number of computer lab PCs", example=200)
    pc_watts: int = Field(default=150, ge=0, description="Average power consumption of one PC in Watts", example=150)
    hours_saved_per_day: float = Field(default=3.0, ge=0, description="Hours PCs are turned off earlier each day", example=3.0)
    working_days_per_month: int = Field(default=22, ge=0, description="College working days per month", example=22)
    solar_kw: float = Field(default=0.0, ge=0, description="Rooftop solar capacity to add in kW", example=20.0)
    led_tubes_replaced: int = Field(default=0, ge=0, description="Number of old 40W fluorescent tubes replaced by 18W LED", example=150)
    led_hours_per_day: float = Field(default=8.0, ge=0, description="Operating hours of lights per day", example=8.0)


class WhatIfAction(BaseModel):
    """Individual action breakdown in what-if simulation."""
    name: str = Field(description="Action name", example="Switch off lab PCs earlier")
    kwh_per_month: float = Field(description="Electricity saved per month in kWh", example=1980.0)
    co2_kg_per_month: float = Field(description="CO2 reduction per month in kg", example=1405.8)
    inr_per_month: float = Field(description="Money saved per month in ₹", example=22770.0)


class WhatIfResponse(BaseModel):
    """Complete response returned by What-If simulator."""
    actions: List[WhatIfAction]
    total_kwh_per_month: float
    total_co2_kg_per_month: float
    total_inr_per_month: float
    total_co2_tonnes_per_year: float
    total_inr_per_year: float
    solar_payback_years: float
    summary: str


# ---------------------------------------------------------
# Mess Meal Schemas
# ---------------------------------------------------------
class MealOut(BaseModel):
    """Schema for an individual mess meal item."""
    id: int
    day: str
    slot: str
    meal_name: str
    meal_type: str
    co2_per_plate: float
    label: str
    color: str
    votes: int


class MessResponse(BaseModel):
    """Schema returned for the weekly mess menu."""
    days: dict
    weekly_co2_kg: float
    green_day_tip: str


# ---------------------------------------------------------
# Anomaly Alert Schema
# ---------------------------------------------------------
class AnomalyItem(BaseModel):
    """Schema representing an anomaly detected for a department."""
    department: str
    this_month_kwh: float
    average_kwh: float
    percent_change: float
    z_score: float
    extra_co2_kg: float
    extra_inr: float
    severity: str
    message: str


class AnomalyResponse(BaseModel):
    """Schema returned for monthly anomaly detection."""
    month: str
    anomalies: List[AnomalyItem]
    message: str
