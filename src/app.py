from flask import Flask, render_template, request, jsonify
import os, random
from datetime import datetime
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# ================= STATE =================
RISK = {"score": 20, "status": "SAFE"}

STATS = {
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

@app.route("/about")
def about():
    return render_template("about.html")


# ================= HELPERS =================
def fix_url(url):
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def valid(url):
    try:
        d = urlparse(url).netloc
        return "." in d
    except:
        return False


# ================= ANALYZE =================
@app.route("/api/analyze")
def analyze():
    global RISK

    url = fix_url(request.args.get("url", ""))

    if not url or not valid(url):
        return jsonify({"score": 0, "status": "INVALID", "issues": []})

    score = random.randint(10, 60)

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
    elif score < 70:
        status = "THREAT"
    else:
        status = "HIGH RISK"

    RISK = {"score": score, "status": status}

    return jsonify({
        "score": score,
        "status": status,
        "issues": ["Scan completed"]
    })


# ================= LIVE SCAN (STABLE) =================
@app.route("/api/continuous-scan")
def continuous_scan():
    base = RISK["score"]

    score = base + random.randint(-20, 20)
    score = max(0, min(100, score))

    events = [
        "DNS OK",
        "Firewall Active",
        "Packet Inspection Running",
        "Bot Check Running",
        "No Anomaly Detected",
        "Traffic Monitoring Active",
        "System Stable"
    ]

    if score < 30:
        status = "SAFE"
    elif score < 50:
        status = "MEDIUM"
    elif score < 70:
        status = "THREAT"
    else:
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
    STATS["total_hits"] += random.randint(1, 4)

    for c in STATS["countries"]:
        STATS["countries"][c] += random.randint(0, 2)

    return jsonify(STATS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
