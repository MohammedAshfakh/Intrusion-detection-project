from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import random
import joblib
import re
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

USERS_FILE = os.path.join(BASE_DIR, "users.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")


# ================= MODEL =================
try:
    model = joblib.load(MODEL_PATH)
except:
    model = None


# ================= GLOBAL STATE =================
CURRENT_URL = ""
CURRENT_RISK = {"status": "SAFE", "score": 10}

ACTIVE_SCAN_SCORE = 10
ACTIVE_SCAN_URL = "Live Network"


VISITOR_STATS = {
    "total_hits": 5,
    "countries": {
        "India": 3,
        "USA": 2,
        "Germany": 1,
        "UK": 1,
        "Japan": 1
    }
}


# ================= USERS =================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r") as f:
            data = f.read().strip()
            return json.loads(data) if data else []
    except:
        return []


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


@app.route("/scan")
def scan():
    if "user" not in session:
        return redirect("/login")
    return render_template("scan.html")


@app.route("/analytics")
def analytics_page():
    return render_template("analytics.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ================= AUTH =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        for u in users:
            if u["email"] == email and u["password"] == password:
                session["user"] = email
                return redirect("/dashboard")

        return "❌ Invalid Credentials"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        users.append({"name": name, "email": email, "password": password})
        save_users(users)

        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= URL HELPERS =================
def normalize_url(url):
    url = url.strip()
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def is_valid_domain(url):
    try:
        domain = urlparse(url).netloc
        return "." in domain and len(domain) > 3
    except:
        return False


# ================= RISK ENGINE =================
def calculate_risk(url):
    score = 10
    issues = []

    if "-" in url:
        score += 10
        issues.append("Suspicious '-' detected")

    if "login" in url.lower():
        score += 15
        issues.append("Login keyword detected")

    if "verify" in url.lower():
        score += 15
        issues.append("Phishing pattern detected")

    if len(url) > 70:
        score += 10
        issues.append("Long URL anomaly")

    score += random.randint(-5, 10)

    return score, issues


# ================= ANALYZE =================
@app.route("/api/analyze")
def analyze():
    global CURRENT_URL, CURRENT_RISK, ACTIVE_SCAN_SCORE, ACTIVE_SCAN_URL, VISITOR_STATS

    url = normalize_url(request.args.get("url", ""))

    if not url or not is_valid_domain(url):
        return jsonify({
            "status": "INVALID URL",
            "score": 0,
            "issues": [],
            "message": "Enter valid domain"
        })

    CURRENT_URL = url
    ACTIVE_SCAN_URL = url
    SCAN_STATE["score"] = score

    VISITOR_STATS["total_hits"] += 1
    country = random.choice(["India", "USA", "Germany", "UK", "Japan"])
    VISITOR_STATS["countries"][country] = VISITOR_STATS["countries"].get(country, 0) + 1

    score, issues = calculate_risk(url)

    if model:
        try:
            pred = model.predict([[len(url), url.count("."), url.count("-"),
                                   url.count("@"), 1, len(re.findall(r"\d", url))]])[0]
            if pred == 1:
                score += 20
                issues.append("ML model flagged anomaly")
        except:
            pass

    score = max(0, min(100, score))

    if score < 30:
        status = "LOW RISK"
    elif score < 70:
        status = "MEDIUM RISK"
    else:
        status = "HIGH RISK"

    CURRENT_RISK = {"status": status, "score": score}
    ACTIVE_SCAN_SCORE = score

    return jsonify({
        "status": status,
        "score": score,
        "issues": issues
    })


# ================= LIVE EVENT =================
@app.route("/api/live-event")
def live_event():
    global ACTIVE_SCAN_SCORE, ACTIVE_SCAN_URL

    ACTIVE_SCAN_SCORE += random.randint(-8, 8)
    ACTIVE_SCAN_SCORE = max(0, min(100, ACTIVE_SCAN_SCORE))

    score = ACTIVE_SCAN_SCORE

    if score < 30:
        status = "SAFE"
        events = ["DNS OK", "Firewall Stable", "No Threat Found"]

    elif score < 50:
        status = "MEDIUM RISK"
        events = ["Suspicious Activity", "Login anomaly detected"]

    elif score < 60:
        status = "THREAT"
        events = ["Bot Activity Detected", "Port Scan Detected"]

    else:
        status = "HIGH RISK"
        events = ["CRITICAL ATTACK", "Data Exfiltration Attempt"]

    return jsonify({
        "type": status,
        "status": status,
        "score": score,
        "url": ACTIVE_SCAN_URL,
        "time": datetime.now().strftime("%H:%M:%S"),
        "event": random.choice(events) if events else "System Active"
    })



@app.route("/api/continuous-scan")
def continuous_scan():
    global SCAN_STATE

    # smooth fluctuation engine
    SCAN_STATE["score"] += random.randint(-12, 12)
    SCAN_STATE["score"] = max(0, min(100, SCAN_STATE["score"]))

    score = SCAN_STATE["score"]

    # severity engine
    if score < 30:
        status = "SAFE"
        events = [
            "DNS OK",
            "Firewall Stable",
            "No Threat Found",
            "Network Clean"
        ]

    elif score < 50:
        status = "MEDIUM RISK"
        events = [
            "Suspicious traffic detected",
            "Login anomaly detected",
            "Port scan activity"
        ]

    elif score < 60:
        status = "THREAT"
        events = [
            "Bot activity detected",
            "Malicious pattern found",
            "Unauthorized request blocked"
        ]

    else:
        status = "HIGH RISK"
        events = [
            "CRITICAL ATTACK DETECTED",
            "Data exfiltration attempt",
            "Ransomware behavior detected"
        ]

    return jsonify({
        "score": score,
        "status": status,
        "event": random.choice(events),
        "time": datetime.now().strftime("%H:%M:%S"),
        "url": SCAN_STATE["url"]
    })


# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics():
    global VISITOR_STATS

    VISITOR_STATS["total_hits"] += random.randint(2, 5)

    for c in VISITOR_STATS["countries"]:
        VISITOR_STATS["countries"][c] += random.randint(1, 3)

    return VISITOR_STATS


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
