FROM python:3.10-slim

# Install system dependencies for Tesseract OCR (multilingual: eng, mar, hin)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-mar \
    tesseract-ocr-hin \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose default port
EXPOSE 8000

# Run Uvicorn server serving both backend APIs and frontend pages
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
