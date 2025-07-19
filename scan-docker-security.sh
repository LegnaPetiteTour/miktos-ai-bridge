#!/bin/bash
# Docker Security Scanner Script
# Usage: ./scan-docker-security.sh

set -e

echo "🔒 Docker Security Scanner for Miktos AI Bridge"
echo "================================================"

# Build the images
echo "📦 Building Docker images..."
echo "🔨 Building development image (Dockerfile)..."
docker build -t miktos-ai-bridge-dev -f Dockerfile .

echo "🔨 Building production image (Dockerfile.production)..."
docker build -t miktos-ai-bridge-prod -f Dockerfile.production .

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
echo "🔍 Scanning development image for vulnerabilities..."
trivy image --severity HIGH,CRITICAL miktos-ai-bridge-dev

echo "🔍 Scanning production image for vulnerabilities..."
trivy image --severity HIGH,CRITICAL miktos-ai-bridge-prod

# Run configuration scan
echo "🔧 Scanning development Dockerfile configuration..."
trivy config Dockerfile

echo "🔧 Scanning production Dockerfile configuration..."
trivy config Dockerfile.production

# Check for secrets
echo "🔐 Scanning for secrets..."
trivy fs --scanners secret .

echo ""
echo "✅ Security scan complete!"
echo "💡 Note: The builder stage vulnerabilities are expected and don't affect the final image."
echo "💡 The distroless runtime image provides enhanced security by minimizing the attack surface."
echo "💡 Tip: Use 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image IMAGE_NAME' for latest Trivy"
