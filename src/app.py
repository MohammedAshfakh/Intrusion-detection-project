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

# ================= LOAD MODEL =================
try:
    model = joblib.load(MODEL_PATH)
except:
    model = None

# ================= USER SYSTEM =================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    return json.load(open(USERS_FILE))

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
def analytics_page():
    return render_template("analytics.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ================= AUTH =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = load_users()

        for u in users:
            if u["email"] == email and u["password"] == password:
                session["user"] = email
                return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()

        users.append({
            "name": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"]
        })

        save_users(users)
        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= ML ANALYSIS =================
@app.route("/api/analyze")
def analyze():
    url = request.args.get("url", "")

    if model:
        features = extract_features(url)

        pred = model.predict(features)[0]

        confidence = 0.6
        if hasattr(model, "predict_proba"):
            confidence = max(model.predict_proba(features)[0])

        if pred == 0:
            status = "SAFE"
            score = int((1 - confidence) * 40)
        else:
            status = "ATTACK"
            score = int(confidence * 100)
    else:
        status = "NO MODEL"
        score = 50

    return jsonify({
        "url": url,
        "status": status,
        "score": score,
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ================= LIVE EVENT =================
@app.route("/api/live-event")
def live_event():

    safe_events = [
        "DNS request resolved successfully",
        "HTTPS handshake verified",
        "No anomaly detected"
    ]

    threat_events = [
        "SQL Injection pattern detected",
        "Brute force attempt blocked",
        "Suspicious redirect found",
        "Malicious payload signature matched"
    ]

    msg = random.choice(safe_events + threat_events)

    return jsonify({
        "message": msg,
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics():
    return jsonify({
        "total_hits": random.randint(100, 500),
        "countries": {
            "India": random.randint(20, 100),
            "USA": random.randint(10, 80),
            "Germany": random.randint(5, 50),
            "Japan": random.randint(5, 40)
        }
    })

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
