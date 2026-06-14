from flask import Flask, render_template, session, request, jsonify
import json, os, random
from datetime import datetime
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# ================= STATE =================
CURRENT_RISK = {"score": 25, "status": "SAFE"}

VISITOR_STATS = {
    "total_hits": 120,
    "countries": {
        "India": 45,
        "USA": 30,
        "Germany": 20,
        "Japan": 15,
        "UK": 10
    }
}


# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
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


# ================= HELPERS =================
def normalize(url):
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def valid(url):
    try:
        return "." in urlparse(url).netloc
    except:
        return False


# ================= ANALYZE (DASHBOARD CORE) =================
@app.route("/api/analyze")
def analyze():
    global CURRENT_RISK

    url = normalize(request.args.get("url", ""))

    if not url or not valid(url):
        return jsonify({"score": 0, "status": "INVALID URL", "issues": []})

    score = random.randint(20, 60)

    if "login" in url.lower():
        score += 10
    if "verify" in url.lower():
        score += 15
    if "-" in url:
        score += 10

    score = max(0, min(100, score))

    if score < 30:
        status = "SAFE"
    elif score < 50:
        status = "MEDIUM RISK"
    elif score < 70:
        status = "THREAT"
    else:
        status = "HIGH RISK"

    CURRENT_RISK = {"score": score, "status": status}

    return jsonify({
        "score": score,
        "status": status,
        "issues": ["Scan completed"]
    })


# ================= 🔥 DASHBOARD LIVE FEED (RESTORED OLD STYLE) =================
@app.route("/api/live-event")
def live_event():
    base = CURRENT_RISK["score"]
    score = max(0, min(100, base + random.randint(-15, 15)))

    safe = ["No anomaly detected", "System stable", "Traffic normal"]
    medium = ["Bot activity detected", "Unusual traffic spike"]
    threat = ["Suspicious payload detected", "Login anomaly detected"]
    high = ["CRITICAL ALERT", "Possible intrusion detected"]

    if score < 30:
        status = "safe"
        msg = random.choice(safe)
    elif score < 50:
        status = "medium"
        msg = random.choice(medium)
    elif score < 70:
        status = "threat"
        msg = random.choice(threat)
    else:
        status = "high"
        msg = random.choice(high)

    return jsonify({
        "type": status,
        "message": msg,          # 👈 IMPORTANT FIX
        "time": datetime.now().strftime("%H:%M:%S"),
        "score": score
    })

# ================= SCAN PAGE ONLY =================
@app.route("/api/continuous-scan")
def continuous_scan():

    score = random.randint(10, 95)

    events = [
        "Packet inspection running",
        "Firewall check active",
        "DNS monitoring active",
        "Traffic scan running",
        "Bot detection active"
    ]

    return jsonify({
        "score": score,
        "event": random.choice(events),
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ================= USERS FILE =================


USERS_FILE = os.path.join(BASE_DIR, "users.json")


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


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # prevent crash duplicates
        for u in users:
            if u["email"] == email:
                return "User already exists"

        users.append({
            "name": name,
            "email": email,
            "password": password
        })

        save_users(users)
        return redirect("/login")

    return render_template("register.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()

        email = request.form.get("email")
        password = request.form.get("password")

        for u in users:
            if u["email"] == email and u["password"] == password:
                session["user"] = email
                return redirect("/dashboard")

        return "Invalid credentials"

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= ANALYTICS =================
@app.route("/api/analytics")
def analytics_api():
    global VISITOR_STATS

    VISITOR_STATS["total_hits"] += random.randint(1, 4)

    for c in VISITOR_STATS["countries"]:
        VISITOR_STATS["countries"][c] += random.randint(0, 2)

    return jsonify(VISITOR_STATS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
