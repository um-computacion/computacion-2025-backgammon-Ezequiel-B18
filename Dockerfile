# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for pygame
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create non-privileged user
RUN useradd -m -u 10001 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose ports
EXPOSE 5000 8000

# Run the Flask server by default
CMD ["python", "-m", "server.main"]