# report_service.py - Generates an audit-ready NAAC Criterion 7 / NIRF Sustainability PDF report.
# Uses ReportLab with clean typography, tables, and executive summary.

import os
import datetime
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from models import Department, MonthlyUsage
from services.anomaly_service import detect_monthly_anomalies
from services.carbon_service import format_inr
from config import GRID_FACTOR, SOLAR_HOURS


def generate_naac_pdf(db: Session, target_month: str, output_path: str) -> str:
    """
    Builds a professional NAAC/NIRF Sustainability Report PDF for the selected month.
    Inputs: db (Session), target_month (str, e.g. '2026-10'), output_path (str)
    Output: output_path (str)
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1b5e20"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#37474f"),
        spaceAfter=14
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2e7d32"),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#212121")
    )

    # 1. Header & Title
    generation_date = datetime.date.today().strftime("%d %B %Y")
    story.append(Paragraph("Green Campus Sustainability Report", title_style))
    story.append(Paragraph(
        f"<b>Nashik College of Engineering — NAAC Criterion 7 / NIRF</b><br/>"
        f"Audit Month: <b>{target_month}</b> &nbsp;|&nbsp; Generated on: {generation_date}",
        subtitle_style
    ))
    story.append(Spacer(1, 8))

    # 2. Campus Summary
    # Fetch all records for target month
    current_records = db.query(MonthlyUsage).filter(MonthlyUsage.month == target_month).all()
    total_kwh = sum([r.units_kwh for r in current_records])
    total_co2_kg = sum([r.co2_kg for r in current_records])
    total_co2_tonnes = round(total_co2_kg / 1000.0, 1)
    total_inr = sum([r.amount_inr for r in current_records])

    # Compare with previous month
    distinct_months = db.query(MonthlyUsage.month).filter(MonthlyUsage.month <= target_month).distinct().order_by(MonthlyUsage.month.desc()).all()
    all_months = [m[0] for m in distinct_months]
    prev_month_str = all_months[1] if len(all_months) > 1 else None

    change_text = "N/A"
    if prev_month_str:
        prev_records = db.query(MonthlyUsage).filter(MonthlyUsage.month == prev_month_str).all()
        prev_kwh = sum([r.units_kwh for r in prev_records])
        if prev_kwh > 0:
            diff_pct = round(((total_kwh - prev_kwh) / prev_kwh) * 100.0, 1)
            sign = "+" if diff_pct > 0 else ""
            change_text = f"{sign}{diff_pct}% vs {prev_month_str}"

    summary_text = (
        f"<b>Executive Summary:</b> During <b>{target_month}</b>, the campus consumed a total of "
        f"<b>{int(round(total_kwh)):,} kWh</b> of electricity, resulting in <b>{total_co2_tonnes} tonnes of CO2</b> emissions "
        f"and an expenditure of <b>Rs. {int(round(total_inr)):,}</b> ({change_text})."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))

    # 3. Department Breakdown Table
    story.append(Paragraph("1. Department-wise Electricity & Carbon League", h2_style))
    dept_table_data = [
        ["Department", "Students", "kWh", "CO2 (kg)", "CO2 / Student", "Bill (Rs.)"]
    ]

    for r in current_records:
        dept_name = r.department.name if r.department else "Unknown"
        dept_students = r.department.students if r.department and r.department.students else 100
        co2_per_student = round(r.co2_kg / dept_students, 1)
        dept_table_data.append([
            dept_name,
            str(dept_students),
            f"{int(round(r.units_kwh)):,}",
            f"{round(r.co2_kg, 1):,}",
            f"{co2_per_student} kg",
            f"Rs. {int(round(r.amount_inr)):,}"
        ])

    dept_table = Table(dept_table_data, colWidths=[120, 55, 75, 75, 85, 90])
    dept_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2e7d32")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd8dc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f8e9")])
    ]))
    story.append(dept_table)
    story.append(Spacer(1, 10))

    # 4. Six-Month Trend Table
    story.append(Paragraph("2. Campus Consumption Trend (Last 6 Months)", h2_style))
    trend_table_data = [
        ["Month", "Total kWh", "CO2 (kg)", "Expenditure (Rs.)"]
    ]

    recent_6_months = list(reversed(all_months[:6]))
    for m in recent_6_months:
        m_recs = db.query(MonthlyUsage).filter(MonthlyUsage.month == m).all()
        m_kwh = sum([x.units_kwh for x in m_recs])
        m_co2 = sum([x.co2_kg for x in m_recs])
        m_inr = sum([x.amount_inr for x in m_recs])
        trend_table_data.append([
            m,
            f"{int(round(m_kwh)):,}",
            f"{round(m_co2, 1):,}",
            f"Rs. {int(round(m_inr)):,}"
        ])

    trend_table = Table(trend_table_data, colWidths=[100, 120, 120, 160])
    trend_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#37474f")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd8dc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#eceff1")])
    ]))
    story.append(trend_table)
    story.append(Spacer(1, 10))

    # 5. Anomalies Section
    story.append(Paragraph("3. Detected Anomalies & Energy Spikes", h2_style))
    anomalies = detect_monthly_anomalies(db, target_month)
    if anomalies:
        for a in anomalies:
            anomaly_desc = f"• <b>{a['department']}</b>: {a['message']}"
            story.append(Paragraph(anomaly_desc, body_style))
    else:
        story.append(Paragraph("• No statistical anomalies detected this month. Usage is within expected limits.", body_style))
    story.append(Spacer(1, 10))

    # 6. Recommended Actions & Solar Tip
    story.append(Paragraph("4. Recommended Sustainability Actions", h2_style))
    story.append(Paragraph(
        f"• <b>Solar Timing Optimization:</b> Schedule heavy loads (e.g. water pumping, laundry) between "
        f"<b>{SOLAR_HOURS}</b> when grid solar generation peaks, reducing reliance on thermal power.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Computer Lab Automation:</b> Power down 200 lab workstations after classes to save up to 1,980 kWh/month.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Hostel Mess Green Day:</b> Introduce weekly Green Day meal pledges to eliminate high-emission mutton/chicken plates.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # 7. Methodology & Official Sources
    story.append(Paragraph("5. Methodology & Compliance Sources", h2_style))
    methodology_text = (
        f"1. Electricity CO2 Baseline: <b>{GRID_FACTOR} kg CO2/kWh</b> sourced from Central Electricity Authority (CEA), "
        f"Ministry of Power, Govt. of India (CO2 Baseline Database for the Indian Power Sector).<br/>"
        f"2. Food Emission Factors: Poore, J., & Nemecek, T. (2018). 'Reducing food's environmental impacts through producers and consumers', Science.<br/>"
        f"3. Compliance Standard: Aligned with NAAC Criterion 7 (Institutional Values and Best Practices) & NIRF Sustainability Indicators."
    )
    story.append(Paragraph(methodology_text, body_style))

    # Build the document
    doc.build(story)
    return output_path
