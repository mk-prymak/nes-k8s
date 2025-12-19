#!/bin/bash
set -e

echo "Starting port-forwarding for NES services..."
echo "You can leave this script running in the background."
echo ""
echo "Access URLs:"
echo "- NES UI:    http://localhost:30000"
echo "- Grafana:   http://localhost:30001"
echo ""
echo "MQTT Broker:"
echo "- TCP:        localhost:1883 (for the external simulator)"
echo "- Websockets: localhost:9001 (optional/debugging)"
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

kubectl port-forward -n nes svc/coordinator 8081:8081 &
PID_COORDINATOR=$!
echo "Forwarding Coordinator (PID $PID_COORDINATOR)..."

kubectl port-forward -n nes svc/mosquitto 1883:1883 &
PID_MOSQUITTO_TCP=$!
echo "Forwarding Mosquitto TCP (PID $PID_MOSQUITTO_TCP)..."

kubectl port-forward -n nes svc/mosquitto 9001:9001 &
PID_MOSQUITTO=$!
echo "Forwarding Mosquitto Websockets (PID $PID_MOSQUITTO)..."

kubectl port-forward -n nes svc/mosquitto 9001:9001 &
PID_MOSQUITTO=$!
echo "Forwarding Mosquitto (PID $PID_MOSQUITTO)..."

echo ""
echo "Press Ctrl+C to stop all port-forwards."

# Wait for user interrupt
trap "kill $PID_UI $PID_GRAFANA $PID_COORDINATOR $PID_MOSQUITTO_TCP $PID_MOSQUITTO; echo 'Stopped port-forwards.'; exit" INT
wait

