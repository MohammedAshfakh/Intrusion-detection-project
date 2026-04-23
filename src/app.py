from flask import Flask, render_template, request
import numpy as np
import joblib

app = Flask(__name__)

model = joblib.load("model.pkl")

attack_count = 0
normal_count = 0

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html",
                           attack=attack_count,
                           normal=normal_count)

@app.route('/monitor', methods=['GET', 'POST'])
def monitor():
    global attack_count, normal_count

    result = None

    if request.method == 'POST':
        data = np.random.rand(10).reshape(1, -1)
        pred = model.predict(data)[0]

        if pred == 1:
            attack_count += 1
            result = "🚨 Attack Detected"
        else:
            normal_count += 1
            result = "✅ Normal Traffic"

        with open("logs.txt", "a") as f:
            f.write(result + "\n")

    return render_template("monitor.html", result=result)

if __name__ == '__main__':
    app.run(debug=True)
