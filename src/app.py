from flask import Flask, render_template, request
import pandas as pd
import pickle
import os
import random

# Configure Flask
app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

# Base project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
RESULTS_PATH = os.path.join(BASE_DIR, "results", "predictions.txt")

# Load trained model
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Dashboard page
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


# About page
@app.route("/about")
def about():
    return render_template("about.html")


# Upload page
@app.route("/upload")
def upload():
    return render_template("upload.html")


# Prediction route
@app.route("/predict", methods=["POST"])
def predict():

    try:

        if "file" not in request.files:
            return "No file uploaded"

        file = request.files["file"]

        if file.filename == "":
            return "No file selected"

        # Read uploaded CSV
        data = pd.read_csv(file)

        # Expected features
        required_columns = ["duration", "src_bytes", "dst_bytes"]

        for col in required_columns:
            if col not in data.columns:
                return f"CSV must contain column: {col}"

        # Select features
        data = data[required_columns]

        # Make prediction
        prediction = model.predict(data)

        if prediction[0] == 1:
            result = "Intrusion Detected"
        else:
            result = "Normal Traffic"

        # Save result to file
        os.makedirs(os.path.join(BASE_DIR, "results"), exist_ok=True)

        with open(RESULTS_PATH, "a") as f:
            f.write(f"Prediction: {result}\n")

        return render_template("result.html", prediction_text=result)

    except Exception as e:
        return str(e)


# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
