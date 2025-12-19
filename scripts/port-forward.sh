#!/bin/bash
set -e

echo "Starting port-forwarding for NES services..."
echo "You can leave this script running in the background."
echo ""
echo "Access URLs:"
echo "- NES UI:    http://localhost:30000"
echo "- Grafana:   http://localhost:30001"
echo "- Datatown:  http://localhost:30003"
echo ""

# Kill existing port-forwards if any (simple cleanup)
pkill -f "kubectl port-forward -n nes" || true

# Start port-forwards in background
kubectl port-forward -n nes svc/ui 30000:9000 &
PID_UI=$!
echo "Forwarding UI (PID $PID_UI)..."

kubectl port-forward -n nes svc/grafana 30001:3000 &
PID_GRAFANA=$!
echo "Forwarding Grafana (PID $PID_GRAFANA)..."

kubectl port-forward -n nes svc/datatown 30003:9003 &
PID_DATATOWN=$!
echo "Forwarding Datatown (PID $PID_DATATOWN)..."

echo ""
echo "Press Ctrl+C to stop all port-forwards."

# Wait for user interrupt
trap "kill $PID_UI $PID_GRAFANA $PID_DATATOWN; echo 'Stopped port-forwards.'; exit" INT
wait

