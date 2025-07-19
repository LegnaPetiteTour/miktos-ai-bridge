# Multi-stage build for security
# Builder stage
FROM python:3.11-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt && \
    pip check

# Runtime stage - using distroless for security
FROM gcr.io/distroless/python3-debian12:latest

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Set PATH to include user packages
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "main.py"]
