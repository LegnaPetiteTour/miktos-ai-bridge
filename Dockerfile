# Multi-stage build for security
# Builder stage
# Note: Using alpine for minimal vulnerabilities
FROM python:3.12-alpine AS builder

# Create non-root user for building
RUN addgroup -S builder && adduser -S -G builder builder

# Set working directory
WORKDIR /app

# Install build dependencies with security updates
RUN apk update && apk upgrade && apk add --no-cache \
    git \
    curl \
    build-base \
    linux-headers

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
