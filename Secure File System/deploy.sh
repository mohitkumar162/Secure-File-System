#!/bin/bash

# This script will exit immediately if any command fails
set -e

# Clear display and show header
clear
echo "=========================================================="
echo "    Secure File Management System - Linux Deploy Script   "
echo "=========================================================="

# Step 1: Check if Docker is installed on the Linux system
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

echo "🐳 [1/3] Building the Docker container image..."
# Build the container using the subfolder context
docker build -t secure-file-system:latest "./Secure File Management System"
echo "✅ Docker image built successfully: secure-file-system:latest"

# Step 2: Show how to run the built image locally in Linux
echo ""
echo "🚀 [2/3] Local run commands for Linux:"
echo "To run the application locally on your Linux machine, execute:"
echo "  docker run -d -p 5000:5000 --name secure-file-system-app secure-file-system:latest"
echo "You can then access the app at http://localhost:5000"
echo ""

# Step 3: Check if Kubernetes command line tool (kubectl) is installed
if command -v kubectl &> /dev/null; then
    echo "☸️ [3/3] Kubernetes detected! Deploying manifests..."
    
    # Apply the secret configurations (environment keys)
    kubectl apply -f k8s/secrets.yaml
    
    # Deploy the application pod replicas
    kubectl apply -f k8s/deployment.yaml
    
    # Expose the application via LoadBalancer
    kubectl apply -f k8s/service.yaml
    
    # Apply Ingress configuration for domain routing
    kubectl apply -f k8s/ingress.yaml
    
    echo "✅ Kubernetes manifests applied successfully!"
    echo "   Verify running pods using: kubectl get pods"
else
    echo "ℹ️  Kubernetes CLI (kubectl) not found. Skipping Kubernetes deployment."
fi

echo "=========================================================="
echo "                     Deployment Info Ready                "
echo "=========================================================="
