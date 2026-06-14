from flask import Flask, render_template, request, redirect, jsonify, session
import os, json, random
from datetime import datetime
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "soc_ai_secret_key_123"


# ================= GLOBAL STATE =================
CURRENT_RISK = {"score": 20, "status": "SAFE"}


# ================= ANALYTICS =================
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


# ================= ROUTES =================
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


# ================= URL HELPERS =================
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
    global CURRENT_RISK

    url = normalize(request.args.get("url", ""))

    if not url or not valid(url):
        return jsonify({"status": "INVALID URL", "score": 0, "issues": []})

    score = random.randint(15, 60)

    if "login" in url.lower():
        score += 10
    if "verify" in url.lower():
        score += 15
    if "-" in url:
        score += 10

    score = max(0, min(100, score))

    if score < 30:
        status = "SAFE"
    elif score < 50:
        status = "MEDIUM RISK"
    elif score < 60:
        status = "THREAT"
    else:
        status = "HIGH RISK"

    CURRENT_RISK = {
        "score": score,
        "status": status
    }

    return jsonify({
        "score": score,
        "status": status,
        "issues": ["Scan completed"]
    })


# ================= LIVE SCAN (SIMPLE & STABLE) =================
@app.route("/api/continuous-scan")
def continuous_scan():

    base = CURRENT_RISK["score"]

    score = base + random.randint(-15, 15)
    score = max(0, min(100, score))

    events = [
        "DNS check OK",
        "Traffic scanning active",
        "Firewall monitoring",
        "Packet inspection running",
        "No anomaly detected",
        "Bot scan completed",
        "System stable"
    ]

    status = "SAFE"
    if score >= 30:
        status = "MEDIUM"
    if score >= 50:
        status = "THREAT"
    if score >= 70:
        status = "HIGH RISK"

    return jsonify({
        "score": score,
        "status": status,
        "event": random.choice(events),
        "time": datetime.now().strftime("%H:%M:%S")
    })


# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics_api():

    VISITOR_STATS["total_hits"] += random.randint(1, 3)

    for c in VISITOR_STATS["countries"]:
        VISITOR_STATS["countries"][c] += random.randint(0, 2)

    return jsonify(VISITOR_STATS)


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
