# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

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

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Create non-privileged user
RUN useradd -m -u 10001 appuser && \
    chown -R appuser:appuser /app

USER appuser

# No exposed ports needed (CLI only, Pygame runs locally)

# Use entrypoint script
ENTRYPOINT ["./entrypoint.sh"]