# Multi-stage build for security
# Builder stage
# Note: Vulnerabilities in the builder stage are expected and don't affect the final image
FROM python:3.11-slim-bookworm AS builder

# Create non-root user for building
RUN groupadd -r builder && useradd -r -g builder builder

# Set working directory
WORKDIR /app

# Install build dependencies with security updates
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/*

# Switch to non-root user for dependency installation
USER builder

# Copy requirements first to leverage Docker cache
COPY --chown=builder:builder requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt && \
    pip check

# Runtime stage - using distroless for security
FROM gcr.io/distroless/python3-debian12:latest

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage (from non-root user)
COPY --from=builder /home/builder/.local /root/.local

# Copy application code
COPY . .

# Set PATH to include user packages
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "main.py"]
