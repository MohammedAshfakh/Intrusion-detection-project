from flask import Flask, render_template, request
import numpy as np
import joblib
import os

app = Flask(__name__)

# Load model
model = joblib.load("model.pkl")

# Counters for dashboard
attack_count = 0
normal_count = 0

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global attack_count, normal_count

    if request.method == 'POST':
        try:
            features = []
            for i in range(10):  # 🔁 change if your model has different features
                val = float(request.form[f"f{i}"])
                features.append(val)

            data = np.array(features).reshape(1, -1)
            prediction = model.predict(data)[0]

            # Logging
            with open("logs.txt", "a") as f:
                f.write(str(prediction) + "\n")

            if prediction == 1:
                attack_count += 1
                result = "🚨 Attack Detected"
            else:
                normal_count += 1
                result = "✅ Normal Traffic"

            return render_template("upload.html", result=result)

        except:
            return render_template("upload.html", result="⚠️ Error in input")

    return render_template("upload.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html",
                           attack=attack_count,
                           normal=normal_count)

if __name__ == '__main__':
    app.run(debug=True)
