from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import joblib
import re

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
)

app.secret_key = "secure_ai_soc_key"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# ================= LOAD MODEL =================
model = joblib.load(MODEL_PATH)

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

# ================= ANALYZE =================
@app.route("/api/analyze")
def analyze():
    url = request.args.get("url", "")

    features = extract_features(url)

    pred = model.predict(features)[0]

    confidence = 0.5
    if hasattr(model, "predict_proba"):
        confidence = max(model.predict_proba(features)[0])

    if pred == 0:
        status = "SAFE"
        score = int((1 - confidence) * 40)
    else:
        status = "ATTACK"
        score = int(confidence * 100)

    return jsonify({
        "url": url,
        "status": status,
        "score": score,
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ================= LIVE FEED =================
@app.route("/api/live-event")
def live_event():
    import random

    events_safe = [
        "DNS request resolved",
        "HTTPS connection verified",
        "No anomalies detected"
    ]

    events_threat = [
        "SQL Injection pattern detected",
        "Brute force attempt blocked",
        "Suspicious redirect found"
    ]

    # simple simulated feed
    msg = random.choice(events_safe + events_threat)

    return jsonify({
        "message": msg,
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics():
    return jsonify({
        "users": len(load_users())
    })

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
