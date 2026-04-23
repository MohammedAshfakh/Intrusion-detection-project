from flask import Flask, render_template, jsonify
import pickle
import os
import random

app = Flask(__name__, template_folder="../templates", static_folder="../static")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

attack_count = 0
normal_count = 0


# ✅ KEEP YOUR INDEX PAGE
@app.route("/")
def index():
    return render_template("index.html")


# ✅ KEEP YOUR ABOUT PAGE
@app.route("/about")
def about():
    return render_template("about.html")


# ⭐ NEW GRAPH PAGE
@app.route("/graph")
def graph():
    return render_template("graph.html")


# 🔥 LIVE DATA
@app.route("/live")
def live():
    global attack_count, normal_count

    duration = random.randint(0, 2)
    src_bytes = random.randint(50, 10000)
    dst_bytes = random.randint(10, 500)

    features = [[duration, src_bytes, dst_bytes]]
    prediction = model.predict(features)

    if prediction[0] == 1:
        result = "Intrusion"
        attack_count += 1
    else:
        result = "Normal"
        normal_count += 1

    return jsonify({
        "duration": duration,
        "src": src_bytes,
        "dst": dst_bytes,
        "result": result,
        "attack": attack_count,
        "normal": normal_count
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
