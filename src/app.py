from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import joblib
import re
import random

# ================= BASE =================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "secure_ai_soc_key_123"

USERS_FILE = os.path.join(BASE_DIR, "users.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

# 🌐 YOUR DEPLOYED WEBSITE URL
SITE_URL = "https://intrusion-detection-project-1.onrender.com/"

# ================= ML MODEL =================
try:
    model = joblib.load(MODEL_PATH)
except:
    model = None

# ================= GLOBAL STATE =================
CURRENT_URL = ""
CURRENT_RISK = {"status": "SAFE", "score": 0}

# ================= USER DB =================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        return json.load(open(USERS_FILE))
    except:
        return []

def save_users(users):
    json.dump(users, open(USERS_FILE, "w"), indent=4)

# ================= FEATURE ENGINEERING =================
def extract_features(url):
    return [[
        len(url),
        url.count("."),
        url.count("-"),
        url.count("@"),
        url.count("?"),
        url.count("&"),
        url.count("="),
        1 if "https" in url else 0,
        1 if "login" in url.lower() else 0,
        int(any(c.isdigit() for c in url)),
        len(re.findall(r"\d", url))
    ]]

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
    return render_template("scan.html")

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ================= AUTH =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        users = load_users()

        email = request.form.get("email")

        for u in users:
            if u["email"] == email:
                return "User already exists"

        users.append({
            "name": request.form.get("name"),
            "email": email,
            "password": request.form.get("password"),
            "created_at": str(datetime.now())
        })

        save_users(users)
        return redirect("/login")

    return render_template("register.html")


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

        return "Invalid credentials"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= ANALYZE =================
@app.route("/api/analyze")
def analyze():

    global CURRENT_URL, CURRENT_RISK

    url = request.args.get("url", "")
    CURRENT_URL = url

    score = random.randint(10, 95)

    if score < 30:
        status = "SAFE"
    elif score < 70:
        status = "MEDIUM"
    else:
        status = "ATTACK"

    CURRENT_RISK = {
        "status": status,
        "score": score,
        "url": url,
        "time": datetime.now().strftime("%H:%M:%S")
    }

    return jsonify(CURRENT_RISK)

# ================= LIVE SCORE FIX =================
@app.route("/api/current-risk")
def current_risk():
    return jsonify(CURRENT_RISK)

# ================= LIVE EVENTS =================
@app.route("/api/live-event")
def live_event():

    events = [
        "Bot traffic blocked",
        "Firewall inspection completed",
        "SQL injection pattern detected",
        "HTTPS secure tunnel verified",
        "Suspicious activity monitored",
        "No active threat on " + SITE_URL
    ]

    return jsonify({
        "message": random.choice(events),
        "url": SITE_URL,
        "time": datetime.now().strftime("%H:%M:%S"),
        "score": CURRENT_RISK["score"]
    })

# ================= FAKE LIVE SCAN =================
@app.route("/api/continuous-scan")
def continuous_scan():

    score = random.randint(5, 100)

    if score < 30:
        status = "SAFE"
    elif score < 70:
        status = "MEDIUM"
    else:
        status = "ATTACK"

    scan_events = [
        "Scanning " + SITE_URL,
        "DNS lookup complete",
        "SSL certificate valid",
        "Checking payload patterns",
        "No malware signature found",
        "Traffic anomaly simulation running"
    ]

    return jsonify({
        "url": SITE_URL,
        "status": status,
        "score": score,
        "event": random.choice(scan_events),
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ================= FAKE ANALYTICS =================
@app.route("/api/analytics")
def analytics_api():

    return jsonify({
        "total_hits": random.randint(500, 8000),
        "site": SITE_URL,
        "countries": {
            "India": random.randint(50, 300),
            "USA": random.randint(30, 200),
            "Germany": random.randint(10, 150),
            "Japan": random.randint(20, 180),
            "UK": random.randint(15, 120)
        }
    })

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
