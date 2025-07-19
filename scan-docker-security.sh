#!/bin/bash
# Docker Security Scanner Script
# Usage: ./scan-docker-security.sh

set -e

echo "🔒 Docker Security Scanner for Miktos AI Bridge"
echo "================================================"

# Build the image
echo "📦 Building Docker image..."
docker build -t miktos-ai-bridge-security-test .

# Check if Trivy is installed
if ! command -v trivy &> /dev/null; then
    echo "⚠️  Trivy not found. Installing..."
    # Install Trivy (works on macOS with Homebrew)
    if command -v brew &> /dev/null; then
        brew install trivy
    else
        echo "❌ Please install Trivy manually: https://trivy.dev/getting-started/installation/"
        exit 1
    fi
fi

# Run vulnerability scan
echo "🔍 Scanning for vulnerabilities..."
trivy image --severity HIGH,CRITICAL miktos-ai-bridge-security-test

# Run configuration scan
echo "🔧 Scanning Docker configuration..."
trivy config Dockerfile

# Check for secrets
echo "🔐 Scanning for secrets..."
trivy fs --scanners secret .

echo ""
echo "✅ Security scan complete!"
echo "💡 Tip: Use 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image miktos-ai-bridge-security-test' for latest Trivy"
