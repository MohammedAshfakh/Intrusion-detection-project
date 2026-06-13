from flask import Flask, render_template, request, redirect, jsonify
import os
import json
import random
from datetime import datetime
from urllib.parse import urlparse

# ==================================================
# CONFIG
# ==================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

USERS_FILE = os.path.join(BASE_DIR, "users.json")

# ==================================================
# USER FUNCTIONS
# ==================================================

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


# ==================================================
# WEBSITE ANALYSIS
# ==================================================

def analyze_url(url):

    score = 0

    parsed = urlparse(url)

    domain = parsed.netloc.lower()

    # HTTPS check
    if url.startswith("https://"):
        score += 20

    # Domain length
    if len(domain) < 20:
        score += 20
    else:
        score += 5

    # Suspicious words
    suspicious_words = [
        "login",
        "verify",
        "secure",
        "bank",
        "free",
        "gift",
        "update",
        "confirm",
        "account"
    ]

    for word in suspicious_words:
        if word in domain:
            score -= 10

    # Number of dots
    dot_count = domain.count(".")
    if dot_count <= 2:
        score += 20
    else:
        score -= 10

    # Hyphen check
    if "-" in domain:
        score -= 10

    # Random adjustment
    score += random.randint(10, 30)

    if score > 100:
        score = 100

    if score >= 75:
        status = "SAFE"
    elif score >= 50:
        status = "MEDIUM RISK"
    else:
        status = "HIGH RISK"

    return {
        "url": url,
        "score": score,
        "status": status
    }


# ==================================================
# LIVE EVENTS
# ==================================================

SAFE_EVENTS = [
    "SSL Certificate Verified",
    "DNS Resolution Successful",
    "Normal Traffic Pattern",
    "Secure HTTPS Connection",
    "Traffic Flow Stable",
    "No Suspicious Activity Found",
    "Firewall Operational",
    "Connection Authenticated"
]

THREAT_EVENTS = [
    "SQL Injection Signature Detected",
    "Suspicious Request Pattern",
    "Brute Force Attempt Detected",
    "Potential XSS Payload Found",
    "Port Scanning Activity",
    "Abnormal Traffic Spike",
    "Unauthorized Access Attempt",
    "Malicious Header Signature"
]


@app.route('/api/live-event')
def live_event():

    if random.random() > 0.75:

        return jsonify({
            "type": "threat",
            "message": random.choice(THREAT_EVENTS),
            "time": datetime.now().strftime("%H:%M:%S")
        })

    return jsonify({
        "type": "safe",
        "message": random.choice(SAFE_EVENTS),
        "time": datetime.now().strftime("%H:%M:%S")
    })


@app.route('/api/analyze')
def analyze():

    url = request.args.get("url", "").strip()

    if not url:
        return jsonify({
            "error": "URL required"
        })

    result = analyze_url(url)

    return jsonify(result)


# ==================================================
# PAGES
# ==================================================

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/about')
def about():
    return render_template("about.html")


# ==================================================
# LOGIN
# ==================================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        for user in users:

            if (
                user["email"] == email and
                user["password"] == password
            ):
                return redirect('/dashboard')

        return """
        <h2 style='font-family:Arial'>
        ❌ Invalid Login
        </h2>
        <a href='/login'>Try Again</a>
        """

    return render_template("login.html")


# ==================================================
# REGISTER
# ==================================================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        for user in users:

            if user["email"] == email:
                return """
                <h2>User already exists</h2>
                <a href='/register'>Go Back</a>
                """

        users.append({
            "name": name,
            "email": email,
            "password": password
        })

        save_users(users)

        return redirect('/login')

    return render_template("register.html")


# ==================================================
# HEALTH CHECK
# ==================================================

@app.route('/health')
def health():
    return {
        "status": "running",
        "application": "AI Website Security Monitor"
    }


# ==================================================
# RUN
# ==================================================

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
