"""
Agent COLLECTOR — Mini SOC Agentique
Rôle : Réceptionner et centraliser les événements du SENSOR
Les stocker et les transmettre à l'ANALYZER
"""

from flask import Flask, request, jsonify
import requests, json, os
from datetime import datetime

app = Flask(__name__)

AUTH_TOKEN = "soc-secret-token-2024"
ANALYZER_URL = "http://127.0.0.1:6002/analyze"
events_store = []

def check_auth(req):
    return req.headers.get("X-Auth-Token") == AUTH_TOKEN

@app.route("/collect", methods=["POST"])
def collect():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    event = request.get_json()
    if not event:
        return jsonify({"error": "No data"}), 400
    
    event["collected_at"] = datetime.utcnow().isoformat() + "Z"
    events_store.append(event)
    print(f"\n[COLLECTOR] Reçu: {event['type']} | src: {event.get('src','?')} | Total: {len(events_store)}")
    
    # Transmettre à l'Analyzer
    try:
        headers = {"Content-Type": "application/json", "X-Auth-Token": AUTH_TOKEN}
        r = requests.post(ANALYZER_URL, json=event, headers=headers, timeout=10)
        print(f"[COLLECTOR] → ANALYZER: HTTP {r.status_code}")
    except Exception as e:
        print(f"[COLLECTOR] ERREUR envoi ANALYZER: {e}")
    
    return jsonify({"status": "collected", "total": len(events_store)}), 200

@app.route("/events", methods=["GET"])
def get_events():
    return jsonify(events_store)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "events_count": len(events_store)})

if __name__ == "__main__":
    print("[COLLECTOR] Démarrage sur port 6001...")
    app.run(host="0.0.0.0", port=6001, debug=False)