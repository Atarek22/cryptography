#!/bin/bash
# Script de démarrage de tous les agents du Mini SOC
echo "========================================"
echo "   DÉMARRAGE DU MINI SOC AGENTIQUE"
echo "========================================"

cd "$(dirname "$0")"

echo "[*] Démarrage du COLLECTOR (port 6001)..."
python3 collector.py &
COLLECTOR_PID=$!
sleep 1

echo "[*] Démarrage de l'ANALYZER (port 6002)..."
python3 analyzer.py &
ANALYZER_PID=$!
sleep 1

echo "[*] Démarrage du RESPONDER (port 6003)..."
python3 responder.py &
RESPONDER_PID=$!
sleep 2

echo "[*] Démarrage du SENSOR..."
python3 sensor.py

echo ""
echo "========================================"
echo "   MINI SOC - RAPPORT FINAL"
echo "========================================"
curl -s http://127.0.0.1:6003/status | python3 -m json.tool

echo ""
echo "[*] Arrêt des agents..."
kill $COLLECTOR_PID $ANALYZER_PID $RESPONDER_PID 2>/dev/null
echo "[*] Mini SOC arrêté."