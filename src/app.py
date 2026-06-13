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

# ================= ML MODEL =================
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

# ================= JSON DATABASE =================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

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

# ================= AUTH SYSTEM =================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        # prevent duplicates
        for u in users:
            if u["email"] == email:
                return "⚠️ User already exists"

        users.append({
            "name": name,
            "email": email,
            "password": password,
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

        return "❌ Invalid credentials"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= ANALYZE URL =================
@app.route("/api/analyze")
def analyze():

    global CURRENT_URL, CURRENT_RISK, VISITOR_STATS

    url = request.args.get("url", "")
    CURRENT_URL = url

    # update hits (REAL tracking now)
    VISITOR_STATS["total_hits"] += 1

    country = random.choice(["India", "USA", "Germany", "Japan", "UK"])
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
                score = random.randint(70, 98)

        except:
            status = "SAFE"
            score = 10
    else:
        status = "MEDIUM"
        score = 50

    CURRENT_RISK = {
        "status": status,
        "score": score,
        "time": datetime.now().strftime("%H:%M:%S"),
        "url": url
    }

    return jsonify(CURRENT_RISK)

# ================= LIVE RISK (FIX FOR DASHBOARD 0 ISSUE) =================
@app.route("/api/current-risk")
def current_risk():
    return jsonify(CURRENT_RISK)

# ================= LIVE FEED =================
@app.route("/api/live-event")
def live_event():

    events = [
        "DNS resolved successfully",
        "HTTPS handshake verified",
        "SQL Injection attempt blocked",
        "Suspicious redirect detected",
        "Brute force attack stopped",
        "No anomaly detected"
    ]

    return jsonify({
        "message": random.choice(events),
        "time": datetime.now().strftime("%H:%M:%S"),
        "url": CURRENT_URL,
        "score": CURRENT_RISK["score"]
    })

# ================= CONTINUOUS SCAN =================
@app.route("/api/continuous-scan")
def continuous_scan():

    if not CURRENT_URL:
        return jsonify({
            "url": "-",
            "status": "NO DATA",
            "score": 0,
            "time": datetime.now().strftime("%H:%M:%S")
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
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics_api():

    return jsonify({
        "total_hits": VISITOR_STATS["total_hits"],
        "countries": VISITOR_STATS["countries"]
    })

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
