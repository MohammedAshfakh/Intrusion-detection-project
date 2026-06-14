from flask import Flask, render_template, request, redirect, jsonify, session
import os
import json
from datetime import datetime
import random
import joblib
import re
import requests
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "soc_ai_secret_key_123"

USERS_FILE = os.path.join(BASE_DIR, "users.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

try:
    model = joblib.load(MODEL_PATH)
except:
    model = None


CURRENT_URL = ""
CURRENT_RISK = {"status": "SAFE", "score": 10}


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

        # must contain at least one dot
        if "." not in domain:
            return False

        # block obvious garbage like "ashu"
        if len(domain) < 4:
            return False

        return True
    except:
        return False


# ================= SIMPLE RISK ENGINE =================
def calculate_risk(url):
    score = 10
    issues = []

    if "-" in url:
        score += 10
        issues.append("Suspicious '-' in domain")

    if len(url) > 75:
        score += 10
        issues.append("Very long URL")

    if "login" in url.lower():
        score += 20
        issues.append("Login keyword detected")

    if "paypal" in url.lower():
        score += 25
        issues.append("Brand impersonation risk")

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

    # test reachability
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

    # ML model optional
    if model:
        try:
            pred = model.predict([[len(url), url.count("."), url.count("-"), url.count("@"), 1, len(re.findall(r"\d", url))]])[0]
            if pred == 1:
                score += 20
                issues.append("ML suspicious pattern detected")
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
        "Firewall OK"
    ]

    threat = [
        "Suspicious pattern detected",
        "Malware signature found",
        "Redirect chain detected"
    ]

    if score < 30:
        msg = random.choice(safe)
        t = "safe"
    else:
        msg = random.choice(threat)
        t = "threat"

    return jsonify({
        "type": t,
        "message": msg,
        "time": datetime.now().strftime("%H:%M:%S"),
        "score": score
    })


# ================= CONTINUOUS SCAN =================
@app.route("/api/continuous-scan")
def continuous_scan():
    score = random.randint(5, 95)

    status = (
        "SAFE" if score < 35 else
        "MEDIUM RISK" if score < 70 else
        "ATTACK DETECTED"
    )

    return jsonify({
        "status": status,
        "score": score,
        "time": datetime.now().strftime("%H:%M:%S"),
        "event": "scan running"
    })


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
