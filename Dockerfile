FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for cryptg
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create temp directory for media files
RUN mkdir -p /tmp

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV RENDER=true

# Expose port for the web service
EXPOSE 8080

# Command to run the application
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --log-file -
