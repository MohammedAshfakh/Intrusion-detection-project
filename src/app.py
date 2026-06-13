from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import random

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "secret123"

USERS_FILE = os.path.join(BASE_DIR, "users.json")

# ===================== GLOBAL STATE =====================
CURRENT_URL = ""
CURRENT_RISK = {"status": "SAFE", "score": 10}


# ===================== USERS =====================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ===================== ROUTES =====================
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


# ===================== LOGIN =====================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        for user in users:
            if user["email"] == email and user["password"] == password:
                session["user"] = email
                return redirect('/dashboard')

        return "Invalid Login"

    return render_template("login.html")


# ===================== REGISTER =====================
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

        users.append({
            "name": name,
            "email": email,
            "password": password
        })

        save_users(users)

        return redirect('/login')

    return render_template("register.html")


# ===================== LOGOUT =====================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ===================== ANALYZE URL =====================
@app.route("/api/analyze")
def analyze():

    global CURRENT_URL, CURRENT_RISK

    url = request.args.get("url", "")
    CURRENT_URL = url

    score = 0

    if "login" in url or "admin" in url:
        score += 60
    if "@" in url:
        score += 20
    if len(url) > 50:
        score += 20

    if score < 30:
        status = "SAFE"
    elif score < 70:
        status = "MEDIUM RISK"
    else:
        status = "HIGH RISK"

    CURRENT_RISK = {"status": status, "score": score}

    return jsonify(CURRENT_RISK)


# ===================== LIVE FEED =====================
@app.route("/api/live-event")
def live_event():

    status = CURRENT_RISK["status"]
    score = CURRENT_RISK["score"]

    safe_events = [
        "DNS Resolution Successful",
        "Secure HTTPS Connection",
        "Firewall Operational",
        "No Suspicious Activity Found"
    ]

    medium_events = [
        "Unusual Traffic Pattern Detected",
        "Rate Limit Warning Triggered",
        "Multiple Requests Observed"
    ]

    threat_events = [
        "SQL Injection Signature Detected",
        "Brute Force Attempt Detected",
        "Malicious Payload Found",
        "Unauthorized Access Attempt"
    ]

    if status == "SAFE":
        msg = random.choice(safe_events)
        t = "safe"
    elif status == "MEDIUM RISK":
        msg = random.choice(medium_events)
        t = "threat"
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


# ===================== RUN =====================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
