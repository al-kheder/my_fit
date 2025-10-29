FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create startup script that handles PORT variable
RUN echo '#!/bin/bash\nset -e\nPORT=${PORT:-8000}\nexec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"' > /app/start.sh && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Use the startup script
CMD ["/app/start.sh"]