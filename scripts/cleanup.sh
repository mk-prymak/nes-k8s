#!/bin/bash
set -e

echo "Cleaning up NES deployment..."

# Delete the namespace (this deletes all resources within it: deployments, services, configmaps, pods)
if kubectl get namespace nes &> /dev/null; then
    echo "Deleting namespace 'nes'..."
    kubectl delete namespace nes
    echo "Namespace 'nes' deleted."
else
    echo "Namespace 'nes' not found. Nothing to delete."
fi

echo "Cleanup complete!"

