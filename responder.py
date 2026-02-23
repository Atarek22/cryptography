"""
Agent RESPONDER — Mini SOC Agentique
Rôle : Appliquer les actions recommandées par l'ANALYZER
Simule le blocage IP ou la création de tickets d'incident
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json, os

app = Flask(__name__)

AUTH_TOKEN = "soc-secret-token-2024"
blocked_ips = set()
tickets = []

def block_ip(ip, event, analysis):
    blocked_ips.add(ip)
    msg = f"[RESPONDER] *** ACTION: BLOCAGE IP ***\n  status=blocked, ip={ip}\n  severity={analysis['severity']}\n  raison={analysis.get('explanation','N/A')}"
    print(msg)
    return {"action": "block_ip", "status": "blocked", "ip": ip}

def create_ticket(event, analysis):
    ticket_id = f"TKT-{len(tickets)+1:04d}"
    ticket = {
        "id": ticket_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "severity": analysis["severity"],
        "category": analysis["category"],
        "event": event,
        "explanation": analysis.get("explanation",""),
        "status": "OPEN"
    }
    tickets.append(ticket)
    print(f"[RESPONDER] *** ACTION: CRÉATION TICKET ***\n  Ticket ID: {ticket_id}\n  Severity: {analysis['severity']}\n  Catégorie: {analysis['category']}")
    return {"action": "create_ticket", "ticket_id": ticket_id, "status": "created"}

def monitor(event, analysis):
    print(f"[RESPONDER] ACTION: SURVEILLANCE — IP {event.get('src','?')} mise sous monitoring")
    return {"action": "monitor", "status": "watching", "ip": event.get("src","?")}

def escalate(event, analysis):
    print(f"[RESPONDER] *** ACTION: ESCALADE — Alerte critique transmise à l'équipe SOC ***\n  {analysis.get('explanation','')}")
    create_ticket(event, analysis)
    return {"action": "escalate", "status": "escalated"}

@app.route("/respond", methods=["POST"])
def respond():
    if request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    
    event = data.get("original_event", {})
    action = data.get("recommended_action", "monitor")
    src_ip = event.get("src", "unknown")
    
    print(f"\n[RESPONDER] Réception: action={action} | IP={src_ip}")
    
    result = {}
    if action == "block_ip":
        result = block_ip(src_ip, event, data)
    elif action == "create_ticket":
        result = create_ticket(event, data)
    elif action == "escalate":
        result = escalate(event, data)
    else:
        result = monitor(event, data)
    
    result["responded_at"] = datetime.utcnow().isoformat() + "Z"
    return jsonify(result), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "blocked_ips": list(blocked_ips),
        "tickets": tickets,
        "total_blocked": len(blocked_ips),
        "total_tickets": len(tickets)
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print("[RESPONDER] Démarrage sur port 6003...")
    app.run(host="0.0.0.0", port=6003, debug=False)