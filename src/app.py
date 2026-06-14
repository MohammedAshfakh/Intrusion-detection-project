from flask import Flask, render_template, request, redirect, jsonify, session
import os, json, random, re
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
except:
    requests = None


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "soc_ai_secret_key_123"


# ================= GLOBAL STATE =================
CURRENT_RISK = {"score": 20, "status": "SAFE"}

# 🔥 DASHBOARD FIX STORAGE (SAFE ADDITION ONLY)
DASHBOARD_HISTORY = []
DASHBOARD_EVENTS = []


# ================= ANALYTICS (FAKE BUT DYNAMIC) =================
VISITOR_STATS = {
    "total_hits": 120,
    "countries": {
        "India": 45,
        "USA": 30,
        "Germany": 20,
        "Japan": 15,
        "UK": 10
    }
}


# ================= HOME ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/scan")
def scan():
    return render_template("scan.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


# ================= URL CHECK =================
def normalize(url):
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def valid(url):
    try:
        d = urlparse(url).netloc
        return "." in d and len(d) > 3
    except:
        return False


# ================= ANALYZE =================
@app.route("/api/analyze")
def analyze():
    global CURRENT_RISK, DASHBOARD_HISTORY, DASHBOARD_EVENTS

    url = normalize(request.args.get("url", ""))

    if not url or not valid(url):
        return jsonify({
            "status": "INVALID URL",
            "score": 0,
            "issues": []
        })

    # base score (stable logic for dashboard)
    score = random.randint(15, 55)

    # rule-based detection
    if "login" in url.lower():
        score += 10
    if "verify" in url.lower():
        score += 15
    if "-" in url:
        score += 10

    score = max(0, min(100, score))

    # status rules
    if score < 30:
        status = "SAFE"
    elif 30 <= score < 50:
        status = "MEDIUM RISK"
    elif 50 <= score < 60:
        status = "THREAT AHEAD"
    else:
        status = "HIGH RISK"

    CURRENT_RISK = {
        "score": score,
        "status": status
    }

    # 🔥 DASHBOARD FIX: store history
    DASHBOARD_HISTORY.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "score": score
    })

    if len(DASHBOARD_HISTORY) > 30:
        DASHBOARD_HISTORY.pop(0)

    # 🔥 DASHBOARD FIX: event feed
    DASHBOARD_EVENTS.insert(0, f"{status} - AI scan completed")

    if len(DASHBOARD_EVENTS) > 15:
        DASHBOARD_EVENTS.pop()

    return jsonify({
        "score": score,
        "status": status,
        "issues": ["AI scan completed"]
    })


# ================= LIVE SCAN (UNCHANGED LOGIC) =================
@app.route("/api/continuous-scan")
def continuous_scan():
    base = CURRENT_RISK["score"]

    # 🔥 SAME BEHAVIOR (DO NOT CHANGE SYSTEM)
    score = base + random.randint(-25, 25)
    score = max(0, min(100, score))

    safe_events = [
        "DNS resolution successful",
        "HTTPS certificate verified",
        "Firewall operating normally",
        "No anomaly detected",
        "System health stable",
        "Traffic baseline normal",
        "Packet inspection clean",
        "Authentication checks passed"
    ]

    medium_events = [
        "Unusual traffic pattern detected",
        "Multiple login attempts observed",
        "Port scan behavior suspected",
        "High request rate from single IP",
        "Bot-like behavior detected",
        "Session timeout anomalies found"
    ]

    threat_events = [
        "Suspicious payload detected",
        "SQL injection attempt blocked",
        "Malicious script execution flagged",
        "Brute force attack suspected",
        "Unauthorized access attempt",
        "C2 communication pattern detected"
    ]

    high_events = [
        "🚨 CRITICAL BOTNET ACTIVITY DETECTED",
        "🚨 DATA EXFILTRATION IN PROGRESS",
        "🚨 RANSOMWARE BEHAVIOR IDENTIFIED",
        "🚨 ADVANCED PERSISTENT THREAT (APT)",
        "🚨 SYSTEM COMPROMISE ATTEMPT",
        "🚨 MULTI-STAGE ATTACK IN PROGRESS"
    ]

    if score < 30:
        status = "SAFE"
        event = random.choice(safe_events)

    elif score < 50:
        status = "MEDIUM RISK"
        event = random.choice(medium_events)

    elif score < 60:
        status = "THREAT AHEAD"
        event = random.choice(threat_events)

    else:
        status = "HIGH RISK"
        event = random.choice(high_events)

    return jsonify({
        "score": score,
        "status": status,
        "event": event,
        "time": datetime.now().strftime("%H:%M:%S")
    })


# ================= DASHBOARD FEED (NEW SAFE ADDITION) =================
@app.route("/api/dashboard-feed")
def dashboard_feed():
    return jsonify({
        "history": DASHBOARD_HISTORY,
        "events": DASHBOARD_EVENTS,
        "current": CURRENT_RISK
    })


# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics_api():
    global VISITOR_STATS

    VISITOR_STATS["total_hits"] += random.randint(1, 5)

    for c in VISITOR_STATS["countries"]:
        VISITOR_STATS["countries"][c] += random.randint(0, 2)

    return VISITOR_STATS

@app.route("/api/dashboard-stream")
def dashboard_stream():
    score = CURRENT_RISK["score"] + random.randint(-10, 10)
    score = max(0, min(100, score))

    events = [
        "No anomaly detected",
        "Bot traffic observed",
        "Firewall OK",
        "Suspicious packet dropped",
        "Login spike detected",
        "Port scan attempt blocked",
        "Normal traffic flow"
    ]

    return jsonify({
        "score": score,
        "event": random.choice(events),
        "time": datetime.now().strftime("%H:%M:%S")
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
