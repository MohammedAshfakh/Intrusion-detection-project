from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import random
import joblib
import re

# OPTIONAL IMPORT (SAFE FALLBACK)
try:
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except:
    REPORTLAB_AVAILABLE = False


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "secret123"

USERS_FILE = os.path.join(BASE_DIR, "users.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

# ================= LOAD MODEL =================
try:
    model = joblib.load(MODEL_PATH)
except:
    model = None

# ================= STATE =================
CURRENT_URL = ""
CURRENT_RISK = {"status": "SAFE", "score": 0}


# ================= USERS =================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ================= PAGES =================
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


@app.route('/about')
def about():
    return render_template("about.html")


# ================= AUTH =================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        for u in users:
            if u["email"] == email and u["password"] == password:
                session["user"] = email
                return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        for u in users:
            if u["email"] == email:
                return "User already exists"

        users.append({"name": name, "email": email, "password": password})
        save_users(users)

        return redirect("/login")

    return render_template("register.html")


@app.route('/logout')
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


# ================= ANALYZE =================
@app.route("/api/analyze")
def analyze():

    global CURRENT_URL, CURRENT_RISK

    url = request.args.get("url", "")
    CURRENT_URL = url

    if model:
        try:
            pred = model.predict(extract_features(url))[0]

            if pred == 0:
                status = "SAFE"
                score = 20
            else:
                status = "ATTACK"
                score = 85
        except:
            status = "SAFE"
            score = 10
    else:
        status = "MEDIUM RISK"
        score = 50

    CURRENT_RISK = {"status": status, "score": score}

    return jsonify(CURRENT_RISK)


# ================= LIVE FEED =================
@app.route("/api/live-event")
def live_event():

    status = CURRENT_RISK["status"]
    score = CURRENT_RISK["score"]

    safe_events = [
        "DNS Resolution Successful",
        "Secure HTTPS Connection",
        "Firewall Operational"
    ]

    attack_events = [
        "SQL Injection Attempt Detected",
        "Brute Force Attack Pattern",
        "Malicious URL Detected",
        "Suspicious Redirect Found"
    ]

    if status == "SAFE":
        msg = random.choice(safe_events)
        t = "safe"
    else:
        msg = random.choice(attack_events)
        t = "threat"

    return jsonify({
        "type": t,
        "message": msg,
        "time": datetime.now().strftime("%H:%M:%S"),
        "url": CURRENT_URL,
        "score": score
    })


# ================= REPORT =================
@app.route("/api/report")
def report():

    if not REPORTLAB_AVAILABLE:
        return jsonify({"error": "reportlab not installed"})

    file_path = os.path.join(BASE_DIR, "static", "report.pdf")

    c = canvas.Canvas(file_path)

    c.drawString(100, 750, "AI Security SOC Report")
    c.drawString(100, 730, f"URL: {CURRENT_URL}")
    c.drawString(100, 710, f"Status: {CURRENT_RISK['status']}")
    c.drawString(100, 690, f"Score: {CURRENT_RISK['score']}")

    c.save()

    return jsonify({"report_url": "/static/report.pdf"})


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
