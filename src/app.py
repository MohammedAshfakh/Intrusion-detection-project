from flask import Flask, render_template, request
import pandas as pd
import pickle
import os
import random

# Flask config
app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Model path
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

# Load model
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    total = random.randint(100, 500)
    attacks = random.randint(10, total // 2)
    normal = total - attacks

    return render_template(
        "dashboard.html",
        total=total,
        attacks=attacks,
        normal=normal
    )


# Upload page
@app.route("/upload")
def upload():
    return render_template("upload.html")


# About page
@app.route("/about")
def about():
    return render_template("about.html")


# Prediction
@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return "No file uploaded"

        file = request.files["file"]

        if file.filename == "":
            return "No file selected"

        data = pd.read_csv(file)

        required_columns = ["duration", "src_bytes", "dst_bytes"]

        for col in required_columns:
            if col not in data.columns:
                return f"CSV must contain column: {col}"

        data = data[required_columns]

        prediction = model.predict(data)

        if prediction[0] == 1:
            result = "Intrusion Detected"
        else:
            result = "Normal Traffic"

        return render_template("result.html", prediction_text=result)

    except Exception as e:
        return str(e)


# Run (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
