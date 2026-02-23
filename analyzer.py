"""
Agent ANALYZER — Mini SOC Agentique
Rôle : Analyser les événements via LM Studio (LLM local)
Classifier la menace et recommander une action au RESPONDER
"""

from flask import Flask, request, jsonify
import requests, json
from datetime import datetime

app = Flask(__name__)

AUTH_TOKEN = "soc-secret-token-2024"
RESPONDER_URL = "http://127.0.0.1:6003/respond"
LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
LM_MODEL = "mistral-7b-instruct"

SYSTEM_PROMPT = """Tu es un expert en cybersécurité SOC (Security Operations Center).
Analyse l'événement de sécurité fourni et réponds UNIQUEMENT en JSON valide avec ce format :
{
  "severity": "Faible|Moyen|Élevé|Critique",
  "category": "brute_force|port_scan|web_attack|malware|suspicious_activity|normal",
  "recommended_action": "block_ip|create_ticket|monitor|ignore|escalate",
  "explanation": "Explication courte en français"
}
Ne mets rien d'autre que le JSON dans ta réponse."""

def analyze_with_llm(event):
    """Envoyer l'événement à LM Studio pour analyse IA"""
    user_message = f"Analyse cet événement de sécurité : {json.dumps(event, ensure_ascii=False)}"
    
    payload = {
        "model": LM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1,
        "max_tokens": 300
    }
    
    try:
        r = requests.post(LM_STUDIO_URL, json=payload, timeout=30)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"].strip()
        # Nettoyer le JSON si nécessaire
        if "```" in content:
            content = content.split("```")[1].replace("json","").strip()
        return json.loads(content)
    except Exception as e:
        print(f"[ANALYZER] Erreur LLM: {e} — utilisation de l'analyse heuristique")
        return heuristic_analyze(event)

def heuristic_analyze(event):
    """Analyse heuristique de secours si LM Studio n'est pas disponible"""
    etype = event.get("type", "")
    
    # Détecter brute force SSH (5+ tentatives)
    if etype == "ssh_failed":
        return {
            "severity": "Élevé",
            "category": "brute_force",
            "recommended_action": "block_ip",
            "explanation": "Tentatives répétées de connexion SSH — probable attaque brute force"
        }
    elif etype == "port_scan":
        return {
            "severity": "Moyen",
            "category": "port_scan",
            "recommended_action": "create_ticket",
            "explanation": "Scan de ports détecté — reconnaissance réseau probable"
        }
    elif etype == "http_anomaly":
        return {
            "severity": "Élevé",
            "category": "web_attack",
            "recommended_action": "block_ip",
            "explanation": "Tentative d'exploitation web (path traversal ou accès admin)"
        }
    elif etype == "dns_query_suspicious":
        return {
            "severity": "Critique",
            "category": "malware",
            "recommended_action": "block_ip",
            "explanation": "Requête DNS vers domaine malveillant connu (C2)"
        }
    elif etype == "malware_hash_detected":
        return {
            "severity": "Critique",
            "category": "malware",
            "recommended_action": "escalate",
            "explanation": "Hash de fichier correspondant à un malware connu"
        }
    else:
        return {
            "severity": "Faible",
            "category": "suspicious_activity",
            "recommended_action": "monitor",
            "explanation": "Activité suspecte à surveiller"
        }

@app.route("/analyze", methods=["POST"])
def analyze():
    if request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    event = request.get_json()
    if not event:
        return jsonify({"error": "No data"}), 400
    
    print(f"\n[ANALYZER] Analyse de: {event.get('type')} depuis {event.get('src','?')}")
    
    # Analyse IA via LM Studio
    analysis = analyze_with_llm(event)
    analysis["analyzed_at"] = datetime.utcnow().isoformat() + "Z"
    analysis["original_event"] = event
    
    print(f"[ANALYZER] Résultat: severity={analysis['severity']} | action={analysis['recommended_action']}")
    
    # Envoyer au Responder
    try:
        headers = {"Content-Type": "application/json", "X-Auth-Token": AUTH_TOKEN}
        r = requests.post(RESPONDER_URL, json=analysis, headers=headers, timeout=5)
        print(f"[ANALYZER] → RESPONDER: HTTP {r.status_code}")
    except Exception as e:
        print(f"[ANALYZER] ERREUR envoi RESPONDER: {e}")
    
    return jsonify({"status": "analyzed", "result": analysis}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print("[ANALYZER] Démarrage sur port 6002...")
    app.run(host="0.0.0.0", port=6002, debug=False)