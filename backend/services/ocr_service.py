# ocr_service.py - Handles bill image processing, multilingual OCR (English, Marathi, Hindi),
# and regex-based extraction of electricity units, bill amount, and billing month.

import os
import re
import time
from PIL import Image, ImageEnhance
import pytesseract
from pdf2image import convert_from_path

from config import GRID_FACTOR
from services.carbon_service import calculate_co2, calculate_cost

# On Windows, Tesseract is commonly installed in Program Files
# Set path automatically if found there and not already in system PATH
if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif os.path.exists(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"


def save_uploaded_file(uploaded_file, destination_folder: str = "uploads") -> str:
    """
    Saves an uploaded file to the uploads folder with a unique timestamp prefix.
    Inputs: uploaded_file (FastAPI UploadFile), destination_folder (str)
    Output: saved_filename (str)
    """
    os.makedirs(destination_folder, exist_ok=True)

    # Prepend unix timestamp to prevent filename collisions
    timestamp = int(time.time())
    safe_filename = f"{timestamp}_{uploaded_file.filename}"
    file_path = os.path.join(destination_folder, safe_filename)

    # Write file content to disk in binary mode
    with open(file_path, "wb") as buffer:
        content = uploaded_file.file.read()
        buffer.write(content)

    return safe_filename


def load_image(file_path: str) -> Image.Image:
    """
    Loads an image from disk. If the file is a PDF, converts the first page into an image.
    Input: file_path (str)
    Output: PIL Image object
    """
    # Check if the file is a PDF document
    if file_path.lower().endswith(".pdf"):
        # Convert first page of PDF into a PIL image
        pages = convert_from_path(file_path, first_page=1, last_page=1)
        if len(pages) > 0:
            return pages[0]
        raise ValueError("Could not extract any page from PDF")

    # If already an image file (PNG/JPG), open directly with Pillow
    return Image.open(file_path)


def clean_image(image: Image.Image) -> Image.Image:
    """
    Enhances an image to improve OCR text recognition accuracy.
    Converts to grayscale, increases contrast by 2x, and scales dimensions by 1.5x.
    Input: image (PIL Image)
    Output: cleaned PIL Image
    """
    # Step 1: Convert to grayscale (removes colored backgrounds and noise)
    gray = image.convert("L")

    # Step 2: Double the contrast so text stands out sharply against the background
    enhancer = ImageEnhance.Contrast(gray)
    high_contrast = enhancer.enhance(2.0)

    # Step 3: Resize image to 1.5x original size to help OCR detect small digits
    width, height = high_contrast.size
    new_width = int(width * 1.5)
    new_height = int(height * 1.5)
    resized = high_contrast.resize((new_width, new_height))

    return resized


def read_text(image: Image.Image) -> str:
    """
    Extracts text from an image using Tesseract OCR with English, Marathi, and Hindi language packs.
    Input: image (PIL Image)
    Output: extracted text string
    """
    try:
        # Feature 2: Supports English (eng), Marathi (mar), and Hindi (hin)
        text = pytesseract.image_to_string(image, lang="eng+mar+hin")
        return text
    except Exception:
        # Fallback to English if regional language packs are not installed
        try:
            return pytesseract.image_to_string(image, lang="eng")
        except Exception:
            # If tesseract engine is missing on the host machine, do not crash
            return ""


def find_units(text: str):
    """
    Searches extracted bill text for electricity consumption in kWh.
    Uses regex patterns for English, Marathi, and Hindi labels.
    Input: text (str)
    Output: tuple (units_kwh as float or None, confidence as 'high' or 'low')
    """
    # Patterns covering English, Marathi and Hindi electricity bill formats (e.g. MSEDCL)
    patterns = [
        r"Units\s*Consumed[^\d\n]*[:=]?\s*([\d,]+(?:\.\d+)?)",
        r"Total\s*Units[^\d\n]*[:=]?\s*([\d,]+(?:\.\d+)?)",
        r"Consumption[^\d\n]*[:=]?\s*([\d,]+(?:\.\d+)?)",
        r"वापर\s*युनिट[^\d\n]*[:=]?\s*([\d,]+(?:\.\d+)?)",
        r"एकूण\s*युनिट[^\d\n]*[:=]?\s*([\d,]+(?:\.\d+)?)",
        r"युनिट[^\d\n]*[:=]?\s*([\d,]+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Clean commas from numbers like '3,076' -> '3076'
            number_string = match.group(1).replace(",", "")
            try:
                units = float(number_string)
                return units, "high"
            except ValueError:
                continue

    return None, "low"


def find_amount(text: str):
    """
    Searches bill text for total payable amount in Indian Rupees (₹).
    Uses regex patterns for English, Marathi, and Hindi labels.
    Input: text (str)
    Output: tuple (amount_inr as float or None, confidence as 'high' or 'low')
    """
    patterns = [
        r"Net\s*Bill\s*Amount[^\d\n₹]*[:=]?\s*₹?\s*([\d,]+(?:\.\d+)?)",
        r"Bill\s*Amount[^\d\n₹]*[:=]?\s*₹?\s*([\d,]+(?:\.\d+)?)",
        r"Total\s*Amount[^\d\n₹]*[:=]?\s*₹?\s*([\d,]+(?:\.\d+)?)",
        r"एकूण\s*रक्कम[^\d\n₹]*[:=]?\s*₹?\s*([\d,]+(?:\.\d+)?)",
        r"रक्कम[^\d\n₹]*[:=]?\s*₹?\s*([\d,]+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            number_string = match.group(1).replace(",", "")
            try:
                amount = float(number_string)
                return amount, "high"
            except ValueError:
                continue

    return None, "low"


def find_month(text: str):
    """
    Searches bill text for the billing month and year.
    Looks for English and Marathi/Hindi month patterns.
    Input: text (str)
    Output: tuple (month_string or None, confidence as 'high' or 'low')
    """
    # Pattern 1: Exact label 'Bill Month: September 2026' or 'बिल महिना: ऑक्टोबर 2026'
    label_pattern = r"(?:Bill\s*Month|बिल\s*महिना)[^\w\n]*([A-Za-z\u0900-\u097F]+\s*\d{4})"
    match = re.search(label_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), "high"

    # Pattern 2: Any English month followed by a 4-digit year
    month_names = "January|February|March|April|May|June|July|August|September|October|November|December"
    date_pattern = rf"\b({month_names})\s+(\d{{4}})\b"
    date_match = re.search(date_pattern, text, re.IGNORECASE)
    if date_match:
        return f"{date_match.group(1)} {date_match.group(2)}", "high"

    return None, "low"


def scan_bill_pipeline(file_path: str, saved_filename: str) -> dict:
    """
    Orchestrates the entire bill reading pipeline: load, clean, OCR, and regex parsing.
    Returns preview data with CO2 and cost calculations.
    Input: file_path (str), saved_filename (str)
    Output: dictionary ready for API response
    """
    raw_text = ""
    try:
        # Load and clean image
        img = load_image(file_path)
        cleaned = clean_image(img)
        # Extract text via OCR
        raw_text = read_text(cleaned)
    except Exception:
        raw_text = ""

    # Parse key electricity bill fields
    units, units_conf = find_units(raw_text)
    amount, amount_conf = find_amount(raw_text)
    bill_month, month_conf = find_month(raw_text)

    # If units were found, calculate preview CO2 and cost
    co2_kg = None
    formula = ""
    if units is not None:
        co2_kg = calculate_co2(units)
        formula = f"{int(units)} kWh × {GRID_FACTOR} kg/kWh (CEA India grid factor)"
        # If amount was not read, estimate it using average tariff
        if amount is None:
            amount = calculate_cost(units)
            amount_conf = "low"
    else:
        formula = f"Units × {GRID_FACTOR} kg/kWh"

    # Determine user-facing message
    if units is not None and amount is not None:
        message = "Bill read successfully. Please check the values before saving."
    else:
        message = "Could not read all bill values clearly. Please type or verify the values."

    return {
        "units_kwh": units,
        "units_confidence": units_conf,
        "amount_inr": amount,
        "amount_confidence": amount_conf,
        "bill_month": bill_month,
        "month_confidence": month_conf,
        "co2_kg": co2_kg,
        "formula": formula,
        "file_name": saved_filename,
        "raw_text": raw_text,
        "message": message
    }
