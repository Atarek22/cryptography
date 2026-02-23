"""
Agent SENSOR — Mini SOC Agentique
Rôle : Détecter et générer des événements de sécurité simulés (logs d'attaque)
Envoie les événements au COLLECTOR via HTTP POST (JSON)
"""

import requests, time, random
from datetime import datetime

COLLECTOR_URL = "http://127.0.0.1:6001/collect"
AUTH_TOKEN = "soc-secret-token-2024"

SIMULATED_EVENTS = [
    {"type": "ssh_failed", "src": "192.168.56.102", "dst": "192.168.56.10", "user": "root"},
    {"type": "ssh_failed", "src": "192.168.56.102", "dst": "192.168.56.10", "user": "admin"},
    {"type": "ssh_failed", "src": "192.168.56.102", "dst": "192.168.56.10", "user": "ubuntu"},
    {"type": "port_scan", "src": "10.0.0.55", "dst": "192.168.56.0/24", "ports": "1-1024"},
    {"type": "ssh_failed", "src": "192.168.56.102", "dst": "192.168.56.10", "user": "postgres"},
    {"type": "http_anomaly", "src": "172.16.0.99", "dst": "192.168.56.20", "path": "/admin/../etc/passwd"},
    {"type": "dns_query_suspicious", "src": "192.168.56.50", "domain": "malware-c2.xyz"},
    {"type": "ssh_failed", "src": "10.10.10.5", "dst": "192.168.56.10", "user": "root"},
    {"type": "port_scan", "src": "10.0.0.55", "dst": "192.168.56.15", "ports": "22,80,443,3389"},
    {"type": "http_anomaly", "src": "172.16.0.99", "dst": "192.168.56.20", "path": "/wp-admin/"},
    {"type": "login_success_unusual", "src": "203.0.113.42", "dst": "192.168.56.30", "user": "jdupont"},
    {"type": "malware_hash_detected", "src": "192.168.56.75", "hash": "d41d8cd98f00b204e9800998ecf8427e"},
]

def send_event(event):
    event["timestamp"] = datetime.utcnow().isoformat() + "Z"
    event["sensor_id"] = "SENSOR-01"
    headers = {"Content-Type": "application/json", "X-Auth-Token": AUTH_TOKEN}
    try:
        r = requests.post(COLLECTOR_URL, json=event, headers=headers, timeout=5)
        print(f"[SENSOR] {event['type']} depuis {event.get('src','?')} → HTTP {r.status_code}")
    except Exception as e:
        print(f"[SENSOR] ERREUR: {e}")

def run_sensor(nb_events=12, interval=2):
    print("="*60)
    print("[SENSOR] Démarrage — envoi d'événements simulés...")
    print("="*60)
    time.sleep(2)
    events = random.sample(SIMULATED_EVENTS, min(nb_events, len(SIMULATED_EVENTS)))
    for i, ev in enumerate(events):
        print(f"\n[SENSOR] Événement {i+1}/{nb_events}:")
        send_event(ev.copy())
        time.sleep(interval)
    print(f"\n[SENSOR] Fin. {nb_events} événements envoyés.")

if __name__ == "__main__":
    run_sensor()