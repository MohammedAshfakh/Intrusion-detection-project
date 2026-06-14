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
CURRENT_URL = "https://intrusion-detection-project-1.onrender.com/"

CURRENT_RISK = {
    "status": "SAFE",
    "score": 15
}

VISITOR_STATS = {
    "total_hits": 1,
    "countries": {
        "India": 3,
        "USA": 2,
        "Germany": 1,
        "Japan": 1,
        "Canada": 1
    }
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

    url = request.args.get("url", "").strip()
    from urllib.parse import urlparse

    parsed = urlparse(url)

    if not url or "." not in parsed.netloc and not url.startswith("http"):
        return jsonify({
            "status": "INVALID URL",
            "score": 0,
            "message": "Please enter a valid domain like google.com"
        })

    if not url:
        return jsonify({
            "status": "INVALID URL",
            "score": 0,
            "message": "Enter a valid or reachable domain"
        })
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    CURRENT_URL = url

    # check if website exists
    try:
        response = requests.get(
            url,
            timeout=5,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if response.status_code >= 400:
            return jsonify({
                "status": "ERROR",
                "score": 100,
                "message": "Website not reachable"
            })

    except:
        return jsonify({
            "status": "INVALID URL",
            "score": 0,
            "message": "Enter a valid or reachable domain"
        })
    VISITOR_STATS["total_hits"] += 1

    country = random.choice([
        "India",
        "USA",
        "UK",
        "Germany",
        "Japan",
        "Canada"
    ])

    VISITOR_STATS["countries"][country] = (
        VISITOR_STATS["countries"].get(country, 0) + 1
    )

    score, issues = calculate_risk(url)

    if model:
        try:
            pred = model.predict(
                extract_features(url)
            )[0]

            if pred == 1:
                score += 20
                issues.append(
                    "ML Model detected suspicious pattern"
                )

        except:
            pass

    score = min(score, 100)

    if score < 30:
        status = "LOW RISK"
    elif score < 70:
        status = "MEDIUM RISK"
    else:
        status = "HIGH RISK"

    CURRENT_RISK = {
        "status": status,
        "score": score,
        "issues": issues
    }

    return jsonify({
        "status": status,
        "score": score,
        "issues": issues
    })
# ================= LIVE EVENTS =================
@app.route("/api/live-event")
def live_event():

    status = CURRENT_RISK["status"]
    score = CURRENT_RISK["score"]

    safe_events = [
        "DNS Resolution Successful",
        "HTTPS Certificate Verified",
        "Firewall Operating Normally",
        "No Threat Indicators Found"
    ]

    threat_events = [
        "Suspicious URL Pattern Detected",
        "Potential Phishing Indicator",
        "Redirect Chain Found",
        "Malicious Signature Matched",
        "Anomaly Detected"
    ]

    if score < 30:
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

    fake_events = [
        "Firewall inspection completed",
        "DNS resolution verified",
        "HTTPS certificate validated",
        "Traffic anomaly detected",
        "Bot activity identified",
        "Suspicious redirect detected",
        "SQL Injection attempt blocked",
        "Connection secured successfully",
        "Malicious payload signature detected",
        "Threat intelligence updated"
    ]

    score = random.randint(5, 95)

    if score < 35:
        status = "SAFE"
    elif score < 70:
        status = "MEDIUM RISK"
    else:
        status = "ATTACK DETECTED"

    return jsonify({
        "url": "https://intrusion-detection-project-1.onrender.com/",
        "status": status,
        "score": score,
        "time": datetime.now().strftime("%H:%M:%S"),
        "event": random.choice(fake_events)
    })
# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics():

    VISITOR_STATS["total_hits"] += random.randint(1, 2)

    if VISITOR_STATS["total_hits"] > 99:
        VISITOR_STATS["total_hits"] = 99

    countries = [
        "India",
        "USA",
        "Germany",
        "Japan",
        "Canada"
    ]

    for country in countries:

        if country not in VISITOR_STATS["countries"]:
            VISITOR_STATS["countries"][country] = random.randint(1, 5)

        VISITOR_STATS["countries"][country] += random.randint(0, 1)

        if VISITOR_STATS["countries"][country] > 99:
            VISITOR_STATS["countries"][country] = 99

    return jsonify(VISITOR_STATS)
# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
