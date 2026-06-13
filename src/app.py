from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import random
import joblib
import re

# ================= BASE PATH =================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "soc_ai_secret_key_123"

USERS_FILE = os.path.join(BASE_DIR, "users.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

# ================= LOAD MODEL =================
try:
    model = joblib.load(MODEL_PATH)
except:
    model = None

# ================= GLOBAL STATE =================
CURRENT_URL = ""
CURRENT_RISK = {"status": "SAFE", "score": 0}

VISITOR_STATS = {
    "total_hits": 0,
    "countries": {}
}

# ================= SAFE JSON HANDLERS =================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []

    try:
        with open(USERS_FILE, "r") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
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

        for u in users:
            if u["email"] == email:
                return "⚠️ User already exists"

        users.append({
            "name": name,
            "email": email,
            "password": password
        })

        save_users(users)

        print("✅ USER SAVED:", email)

        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= FEATURE ENGINEERING =================
def extract_features(url):
    return [[
        len(url),
        url.count("."),
        url.count("-"),
        url.count("@"),
        1 if "https" in url else 0,
        len(re.findall(r"\d", url))
    ]]

# ================= ANALYZE URL =================
@app.route("/api/analyze")
def analyze():
    global CURRENT_URL, CURRENT_RISK, VISITOR_STATS

    url = request.args.get("url", "")
    CURRENT_URL = url

    # fake traffic stats
    VISITOR_STATS["total_hits"] += 1

    country = random.choice(["India", "USA", "UK", "Germany", "Japan", "Canada"])

    VISITOR_STATS["countries"][country] = VISITOR_STATS["countries"].get(country, 0) + 1

    # ML prediction
    if model:
        try:
            pred = model.predict(extract_features(url))[0]

            if pred == 0:
                status = "SAFE"
                score = random.randint(5, 30)
            else:
                status = "ATTACK"
                score = random.randint(70, 95)

        except:
            status = "SAFE"
            score = 10
    else:
        status = "MEDIUM RISK"
        score = 50

    CURRENT_RISK = {"status": status, "score": score}

    return jsonify(CURRENT_RISK)

# ================= LIVE EVENTS =================
@app.route("/api/live-event")
def live_event():

    status = CURRENT_RISK["status"]
    score = CURRENT_RISK["score"]

    safe_events = [
        "DNS Resolution Successful",
        "HTTPS Handshake Verified",
        "Firewall Operating Normally",
        "No Anomaly Detected"
    ]

    threat_events = [
        "SQL Injection Attempt Blocked",
        "Brute Force Attack Detected",
        "Malicious URL Signature Found",
        "Suspicious Redirect Behavior"
    ]

    if status == "SAFE":
        msg = random.choice(safe_events)
        t = "safe"
    else:
        msg = random.choice(threat_events)
        t = "threat"

    return jsonify({
        "type": t,
        "message": msg,
        "time": datetime.now().strftime("%H:%M:%S"),
        "url": CURRENT_URL,
        "score": score
    })

# ================= CONTINUOUS SCAN =================
@app.route("/api/continuous-scan")
def continuous_scan():

    if not CURRENT_URL:
        return jsonify({
            "url": "",
            "status": "NO DATA",
            "score": 0,
            "time": datetime.now().strftime("%H:%M:%S"),
            "event": "No URL selected"
        })

    score = random.randint(10, 95)

    if score < 30:
        status = "SAFE"
    elif score < 70:
        status = "MEDIUM"
    else:
        status = "ATTACK"

    return jsonify({
        "url": CURRENT_URL,
        "status": status,
        "score": score,
        "time": datetime.now().strftime("%H:%M:%S"),
        "event": random.choice([
            "Packet analyzed",
            "Header inspection done",
            "Traffic pattern checked",
            "Anomaly scan running"
        ])
    })

# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics():
    return jsonify(VISITOR_STATS)

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
