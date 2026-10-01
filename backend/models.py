# models.py - Defines the database tables using SQLAlchemy ORM.
# Each class represents a table in the database (carbon.db or Supabase).

import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Department(Base):
    """
    Represents an academic department or campus facility.
    Stores the department name and the number of students enrolled.
    """
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    students = Column(Integer, nullable=False, default=100)

    # Relationships to access related usage history and uploaded bills
    monthly_usages = relationship("MonthlyUsage", back_populates="department", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="department", cascade="all, delete-orphan")


class MonthlyUsage(Base):
    """
    Stores historical monthly electricity consumption for each department.
    Used for overview dashboard, Carbon League leaderboard, and anomaly detection.
    """
    __tablename__ = "monthly_usages"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    month = Column(String(10), nullable=False)  # Example: '2026-10'
    units_kwh = Column(Float, nullable=False)    # Electricity consumption in units (kWh)
    amount_inr = Column(Float, nullable=False)   # Electricity bill cost in Rupees (₹)
    co2_kg = Column(Float, nullable=False)       # Calculated carbon footprint in kg CO2

    # Relationship back to the parent department
    department = relationship("Department", back_populates="monthly_usages")


class Bill(Base):
    """
    Stores electricity bills that users scan and confirm.
    Saves the extracted values, filename, and raw OCR text for audit trails.
    """
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    bill_month = Column(String(50), nullable=False)   # Example: 'September 2026'
    units_kwh = Column(Float, nullable=False)         # Units extracted from bill
    amount_inr = Column(Float, nullable=False)        # Total amount extracted from bill
    co2_kg = Column(Float, nullable=False)            # Calculated CO2 footprint
    file_name = Column(String(255), nullable=False)   # Name of the uploaded file
    raw_text = Column(Text, nullable=True)            # Full text extracted by OCR
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship back to the parent department
    department = relationship("Department", back_populates="bills")


class MessMeal(Base):
    """
    Stores meals served in the campus hostel mess throughout the week.
    Each meal has a type (veg, egg, chicken, mutton) used to calculate carbon score.
    """
    __tablename__ = "mess_meals"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(String(20), nullable=False)         # Monday, Tuesday, ... Sunday
    slot = Column(String(20), nullable=False)        # lunch or dinner
    meal_name = Column(String(100), nullable=False)  # Example: 'Varan Bhaat', 'Chicken Biryani'
    meal_type = Column(String(20), nullable=False)   # veg, egg, chicken, mutton
    votes = Column(Integer, default=0)               # Number of student pledge votes for Green Day
