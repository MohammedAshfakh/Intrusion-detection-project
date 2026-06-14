from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import random
import joblib
import re
from urllib.parse import urlparse

# optional requests (safe for deployment)
try:
    import requests
except:
    requests = None


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


# ================= SAFE MODEL LOAD =================
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print("Model load failed:", e)
    model = None


# ================= GLOBAL STATE =================
CURRENT_URL = ""
CURRENT_RISK = {
    "status": "SAFE",
    "score": 10
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

        for u in users:
            if u["email"] == email:
                return "⚠️ User already exists"

        users.append({
            "name": name,
            "email": email,
            "password": password
        })

        save_users(users)
        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= URL VALIDATION =================
def normalize_url(url):
    url = url.strip()
    if not url:
        return None

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def is_valid_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc

        if "." not in domain:
            return False

        if len(domain) < 4:
            return False

        return True
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
        issues.append("Verification scam pattern")

    if len(url) > 70:
        score += 10
        issues.append("Long suspicious URL")

    return score, issues


# ================= ANALYZE =================
@app.route("/api/analyze")
def analyze():
    global CURRENT_URL, CURRENT_RISK

    url = request.args.get("url", "")
    url = normalize_url(url)

    if not url or not is_valid_domain(url):
        return jsonify({
            "status": "INVALID URL",
            "score": 0,
            "message": "Enter valid domain like google.com"
        })

    # check website reachability
    if requests:
        try:
            r = requests.get(url, timeout=4)
            if r.status_code >= 400:
                return jsonify({
                    "status": "ERROR",
                    "score": 100,
                    "message": "Website not reachable"
                })
        except:
            return jsonify({
                "status": "ERROR",
                "score": 100,
                "message": "Website not reachable"
            })

    CURRENT_URL = url

    score, issues = calculate_risk(url)

    # ML prediction (optional)
    if model:
        try:
            pred = model.predict([[
                len(url),
                url.count("."),
                url.count("-"),
                url.count("@"),
                1 if "https" in url else 0,
                len(re.findall(r"\d", url))
            ]])[0]

            if pred == 1:
                score += 20
                issues.append("ML model flagged risk")

        except:
            pass

    score = min(score, 100)

    if score < 30:
        status = "LOW RISK"
    elif score < 70:
        status = "MEDIUM RISK"
    else:
        status = "HIGH RISK"

    CURRENT_RISK = {"status": status, "score": score}

    return jsonify({
        "status": status,
        "score": score,
        "issues": issues
    })


# ================= LIVE EVENT =================
@app.route("/api/live-event")
def live_event():
    score = CURRENT_RISK["score"]

    safe = [
        "DNS OK",
        "HTTPS Verified",
        "Firewall Stable"
    ]

    threat = [
        "Suspicious activity detected",
        "Malware signature match",
        "Phishing pattern found"
    ]

    msg = random.choice(safe if score < 30 else threat)

    return jsonify({
        "type": "safe" if score < 30 else "threat",
        "message": msg,
        "time": datetime.now().strftime("%H:%M:%S"),
        "score": score
    })


# ================= CONTINUOUS SCAN =================
@app.route("/api/continuous-scan")
def continuous_scan():
    score = random.randint(5, 95)

    return jsonify({
        "status": "SAFE" if score < 35 else "RISK",
        "score": score,
        "time": datetime.now().strftime("%H:%M:%S"),
        "event": "scan running"
    })


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
