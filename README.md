# 🛡️ Mini SOC Agentique — IA Locale (LM Studio / Ollama)

> Système de détection et réponse aux incidents de sécurité automatisé,  
> basé sur 4 agents coopérants et une IA locale (Mistral 7B).

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![LM Studio](https://img.shields.io/badge/LM_Studio-compatible-purple?style=flat-square)
![Ollama](https://img.shields.io/badge/Ollama-compatible-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📋 Description

Ce projet implémente un **Mini SOC (Security Operations Center) Agentique** composé de 4 agents autonomes qui communiquent entre eux via HTTP REST en JSON pour automatiser la détection, l'analyse et la réponse aux incidents de sécurité.

```
[SENSOR] ──► [COLLECTOR] ──► [ANALYZER (IA)] ──► [RESPONDER]
  Port:           6001              6002               6003
```

L'**ANALYZER** interroge un LLM local (via LM Studio ou Ollama) pour classifier chaque menace et recommander une action automatique.

---

## 🏗️ Architecture

| Agent | Port | Rôle |
|-------|------|------|
| **SENSOR** | — | Génère des événements de sécurité simulés (SSH brute force, port scan, etc.) |
| **COLLECTOR** | 6001 | Centralise et horodate les événements, les transmet à l'Analyzer |
| **ANALYZER** | 6002 | Analyse via LLM local, classifie la menace, recommande une action |
| **RESPONDER** | 6003 | Applique l'action : blocage IP, ticket d'incident, escalade |

### Communication
- **Format** : JSON
- **Protocole** : HTTP REST
- **Auth** : Token Bearer (`X-Auth-Token`)
- **LLM API** : OpenAI-compatible (`/v1/chat/completions`)

---

## 📁 Structure du projet

```
mini-soc-agents/
│
├── sensor.py          # Agent SENSOR — génération d'événements
├── collector.py       # Agent COLLECTOR — centralisation (port 6001)
├── analyzer.py        # Agent ANALYZER + IA locale (port 6002)
├── responder.py       # Agent RESPONDER — actions (port 6003)
├── start_all.sh       # Script de démarrage automatique
└── README.md          # Ce fichier
```

---

## ⚙️ Prérequis

- **OS** : Linux (Ubuntu 22.04+ / Kali Linux)
- **Python** : 3.10+
- **LLM** : LM Studio ou Ollama avec Mistral 7B Instruct

### Dépendances Python
```bash
pip3 install flask requests --break-system-packages
```
ou
```bash
sudo apt install python3-flask python3-requests -y
```

---

## 🚀 Installation & Démarrage

### Étape 1 — Cloner le dépôt
```bash
git clone https://github.com/VOTRE_USERNAME/mini-soc-agents.git
cd mini-soc-agents
```

### Étape 2 — Installer les dépendances
```bash
pip3 install flask requests --break-system-packages
```

### Étape 3 — Démarrer le LLM local

**Option A — Ollama (recommandé sur Linux) :**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
ollama serve
```

**Option B — LM Studio :**
```bash
# Télécharger l'AppImage depuis https://lmstudio.ai
chmod +x LM-Studio-*.AppImage
./LM-Studio-*.AppImage --no-sandbox
# Charger Mistral 7B Instruct et démarrer le serveur local (port 1234)
```

### Étape 4 — Vérifier que le LLM répond
```bash
# Ollama
curl http://127.0.0.1:11434/v1/models

# LM Studio
curl http://127.0.0.1:1234/v1/models
```

### Étape 5 — Lancer le Mini SOC
```bash
chmod +x start_all.sh
bash start_all.sh
```

---

## 🔧 Configuration

Dans `analyzer.py`, modifier selon votre LLM :

```python
# Pour Ollama
LM_STUDIO_URL = "http://127.0.0.1:11434/v1/chat/completions"
# model = "mistral"

# Pour LM Studio
LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
# model = "mistral-7b-instruct"
```

---

## 📊 Exemple de flux complet

```
[SENSOR]   ssh_failed depuis 192.168.56.102 → HTTP 200
[COLLECTOR] Reçu: ssh_failed | src: 192.168.56.102 | Total: 1
[COLLECTOR] → ANALYZER: HTTP 200
[ANALYZER] Analyse: ssh_failed depuis 192.168.56.102
[ANALYZER] → severity=Élevé | action=block_ip
[RESPONDER] *** status=blocked, ip=192.168.56.102 ***
```

### Types d'événements simulés

| Type | Sévérité | Action |
|------|----------|--------|
| `ssh_failed` | Élevé | `block_ip` |
| `port_scan` | Moyen | `create_ticket` |
| `http_anomaly` | Élevé | `block_ip` |
| `dns_query_suspicious` | Critique | `block_ip` |
| `malware_hash_detected` | Critique | `escalate` |
| `login_success_unusual` | Faible | `monitor` |

---

## 📡 API Endpoints

### COLLECTOR — port 6001
```bash
POST /collect     # Recevoir un événement
GET  /events      # Lister tous les événements
GET  /health      # Statut du service
```

### ANALYZER — port 6002
```bash
POST /analyze     # Analyser un événement via LLM
GET  /health      # Statut du service
```

### RESPONDER — port 6003
```bash
POST /respond     # Appliquer une action
GET  /status      # IPs bloquées + tickets créés
GET  /health      # Statut du service
```

### Vérifier les résultats après exécution
```bash
# IPs bloquées et tickets créés
curl -s http://127.0.0.1:6003/status | python3 -m json.tool

# Tous les événements collectés
curl -s http://127.0.0.1:6001/events | python3 -m json.tool
```

---

## 🔒 Sécurité (simulation)

Tous les agents utilisent un token d'authentification dans les headers HTTP :
```
X-Auth-Token: soc-secret-token-2024
```
> ⚠️ Token statique — à remplacer par JWT ou mTLS en production.

---

## 📈 Limites & Améliorations possibles

### Limites actuelles
- Stockage en mémoire (données perdues au redémarrage)
- Token d'authentification statique
- Pas de corrélation d'événements (chaque événement analysé indépendamment)
- Latence LLM (2–10 secondes par événement)

### Améliorations suggérées
- [ ] Base de données (PostgreSQL / Elasticsearch)
- [ ] HTTPS + mTLS entre agents
- [ ] Corrélation d'événements (détection de patterns)
- [ ] Dashboard temps réel (Grafana / Kibana)
- [ ] Intégration Threat Intelligence (AbuseIPDB)
- [ ] Interface de supervision humaine (SOAR)
- [ ] File de messages (RabbitMQ / Kafka)

---

## 🧪 TP — Contexte pédagogique

Ce projet a été réalisé dans le cadre d'un **TP — Mini SOC Agentique avec IA Locale (LM Studio)** avec les objectifs suivants :
- Comprendre l'architecture d'un SOC réel
- Découvrir les agents logiciels coopérants
- Intégrer une IA locale pour l'analyse automatique
- Observer le flux complet : détection → analyse → décision → action

**Environnement :**
- VM Ubuntu / Kali Linux (serveur SOC)
- LM Studio ou Ollama avec Mistral 7B Instruct
- Python 3 + Flask + requests

---

## 👨‍💻 Auteur

**Nom :** *Taha El Yacoubi* & *Azzedine lazrarqi*  
**Module :** Cryptography  
**Niveau :** 5th year engineering  
**Année :** 2025–2026

---

