FROM python:3.12-slim

# Install system dependencies including Tesseract OCR & libmupdf support
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create uploads directory
RUN mkdir -p /app/storage/uploads

ENV PYTHONUNBUFFERED=1

EXPOSE 10000

# Render sets $PORT dynamically; default to 10000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
