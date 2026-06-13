# 🛡 AI Security Operations Center (SOC) - Intrusion Detection System

## MCA Project – Andhra University

This project demonstrates how **Machine Learning + Flask Web Development** can be used to build a **Security Operations Center (SOC) style Intrusion Detection System**.

The system analyzes website URLs, simulates cyber attack detection, and displays a **real-time SOC dashboard** with threat intelligence, live scanning, and analytics.

The project is deployed as a web application using **Python Flask** and hosted on **Render Cloud Platform**.

---

# 🌐 Live Project

https://intrusion-detection-project-1.onrender.com/

---

# 👨‍🎓 Developed By

Shaik Tasneem  
Master of Computer Applications (MCA)  
Andhra University  

---

# 👨‍🏫 Project Guide

Mohammed Ashfakh  
Web Developer, Cloud & Cybersecurity Engineer  

---

# 📅 Academic Year

2025 – 2026  

---

--------------------------------------------------

# 💡 Project Objective

The main objective of this project is to simulate a **SOC (Security Operations Center)** environment that:

- Detects malicious URLs using Machine Learning
- Displays real-time threat scores
- Simulates live cyber attack intelligence
- Tracks fake global traffic analytics
- Provides a dashboard for cybersecurity monitoring

---

--------------------------------------------------

# ⚙ System Requirements

## 🖥 Operating System:
- Ubuntu Linux / Windows / MacOS

## 🧠 Software Requirements:
- Python 3.x
- Flask
- Pandas
- NumPy
- Scikit-learn
- Joblib

## 🌐 Browser:
- Google Chrome / Firefox


--------------------------------------------------

# 📁 Project Structure
intrusion-detection-project-ML
│
├── README.md
├── requirements.txt
│
├── dataset/
│ └── dataset.csv (optional training data)
│
├── model/
│ └── model.pkl (trained ML model)
│
├── results/
│ └── predictions.txt
│
├── src/
│ └── app.py (Flask backend + SOC logic)
│
├── templates/
│ ├── index.html
│ ├── dashboard.html
│ ├── scan.html
│ ├── analytics.html
│ └── about.html
│
├── static/
│ ├── style.css
│ └── logo.png
│
├── users.json (simple JSON database)
└── Procfile (Render deployment)


---
-------------------------------------------------------------

# 🚀 Installation & Setup

## 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
2️⃣ Run the application locally
python src/app.py
3️⃣ Open in browser
http://localhost:5000
☁ Deployment (Render)

The project is deployed using Render cloud hosting.

-------------------------------------------------------------
🌐 Live URL:

https://intrusion-detection-project-1.onrender.com/

-------------------------------------------------------------
🧠 How the System Works
User opens the SOC dashboard
User enters a URL for analysis
System generates a threat score using ML/simulation
URL is classified as:
SAFE
MEDIUM RISK
ATTACK
Live SOC feed displays simulated cyber events
Analytics page shows fake global traffic data
Live scan page continuously monitors the URL
-------------------------------------------------------------
🔥 Key Features
🛡 SOC Dashboard
Real-time threat score monitoring
Live attack feed simulation
⚡ URL Threat Detection
ML-based / simulated classification
Risk scoring system (0–100)
🌍 Analytics System
Fake global traffic visualization
Country-wise visitor simulation
📡 Live Scan Module
Continuous scanning every few seconds
Real-time status updates
🔐 Authentication System
User registration and login
JSON-based database (users.json)
-------------------------------------------------------------
🧪 Technologies Used
Backend:
Python
Flask
Machine Learning:
Scikit-learn
Pandas
NumPy
Joblib
Frontend:
HTML5
CSS3
JavaScript
Chart.js
Deployment:
Render Cloud Platform
-------------------------------------------------------------
⚠ Limitations
Traffic data is simulated (not real-world network packets)
No real IDS packet capture
Uses JSON instead of full database system
ML model is simplified for academic use
-------------------------------------------------------------
🚀 Future Enhancements
Real-time packet sniffing (Scapy / Wireshark integration)
WebSocket live updates (no refresh system)
Advanced deep learning intrusion detection
IP geolocation tracking
Admin dashboard panel
Email alert system for threats
Cloud database integration (MongoDB / PostgreSQL)

-------------------------------------------------------------

🎯 Conclusion

This project demonstrates a SOC-style cybersecurity monitoring system using Machine Learning and Flask.

It helps understand:

Intrusion Detection Systems (IDS)
Real-time security monitoring
Cybersecurity analytics
SOC operations in a simulated environment

It is suitable for MCA academic submission and cybersecurity portfolio projects.
---------------------------------------------------------------------------

📌 License

This project is developed for academic purposes as part of MCA program at Andhra University.


