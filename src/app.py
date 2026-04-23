from flask import Flask, render_template, request, redirect
import os
import json

# BASE
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

USERS_FILE = os.path.join(BASE_DIR, "users.json")

# ---------------- USER FUNCTIONS ----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/about')
def about():
    return render_template("about.html")


# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        for user in users:
            if user["email"] == email and user["password"] == password:
                return redirect('/dashboard')

        return "❌ Invalid Login"

    return render_template("login.html")


# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        # duplicate check
        for u in users:
            if u["email"] == email:
                return "⚠️ User already exists"

        users.append({
            "name": name,
            "email": email,
            "password": password
        })

        save_users(users)

        return redirect('/login')

    return render_template("register.html")


# RUN
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
