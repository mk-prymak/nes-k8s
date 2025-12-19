#!/bin/bash
set -e

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl could not be found. Please install it."
    exit 1
fi

# Architecture warning
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    echo "WARNING: You are running on ARM64 architecture."
    echo "The NES Coordinator image is x86_64 only."
    echo "Ensure your Kubernetes cluster supports x86 emulation (e.g., Docker Desktop with Rosetta, or configured QEMU)."
    echo "If the coordinator pod crashes with a segmentation fault, your cluster's emulation configuration is likely insufficient."
    echo "Continuing deployment..."
    sleep 2
fi

echo "Deploying NES to Kubernetes..."

# Apply namespace
echo "Applying namespace..."
kubectl apply -f k8s/00-namespace.yaml

# Apply components
echo "Applying manifests..."
kubectl apply -f k8s/10-nes-coordinator.yaml
kubectl apply -f k8s/20-mosquitto.yaml
kubectl apply -f k8s/30-workers.yaml
kubectl apply -f k8s/40-ui.yaml
kubectl apply -f k8s/60-grafana.yaml

echo "Waiting for pods to be ready (timeout 300s)..."
# We wait for pods to be created first
sleep 5
kubectl wait --for=condition=ready pod --all -n nes --timeout=300s

echo "Deployment complete!"
echo ""
echo "Accessing Services:"
echo "If using Docker Desktop Kubernetes (localhost):"
echo "- NES UI:       http://localhost:30000"
echo "- Grafana:      http://localhost:30001"
echo ""
echo "If using Minikube:"
echo "Run 'minikube service list -n nes' to see the URLs."

