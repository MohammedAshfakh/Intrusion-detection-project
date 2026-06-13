from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import joblib
import re
import random

# ================= BASE SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "secure_ai_soc_key_123"

USERS_FILE = os.path.join(BASE_DIR, "users.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

# ================= LOAD ML MODEL =================
try:
    model = joblib.load(MODEL_PATH)
except:
    model = None

# ================= DATABASE (JSON FILE) =================
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

# ================= AUTH =================

# LOGIN (READ from JSON DB)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        for user in users:
            if user["email"] == email and user["password"] == password:
                session["user"] = email
                return redirect("/dashboard")

        return "❌ Invalid email or password"

    return render_template("login.html")


# REGISTER (WRITE into JSON DB)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        # check duplicate
        for user in users:
            if user["email"] == email:
                return "⚠️ User already exists"

        # append new user
        users.append({
            "name": name,
            "email": email,
            "password": password,
            "created_at": str(datetime.now())
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

# ================= LIVE EVENTS =================
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
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ================= ANALYTICS API =================
@app.route("/api/analytics")
def analytics_api():
    users = load_users()

    return jsonify({
        "total_users": len(users),
        "users": users,
        "countries": {
            "India": random.randint(20, 100),
            "USA": random.randint(10, 70),
            "Germany": random.randint(5, 40),
            "Japan": random.randint(5, 30)
        }
    })

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
