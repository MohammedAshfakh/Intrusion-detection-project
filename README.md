# Machine Learning Based Intrusion Detection System

## MCA Project – Andhra University

This project demonstrates how **Machine Learning** can be used to detect malicious activities in network traffic.
The system analyzes network traffic data and classifies it as either **Normal Traffic** or **Cyber Attack**.

The project is implemented as a **web application using Python Flask** and runs on **Ubuntu Linux (VM environment)**.

---

# Project Title

Machine Learning Based Intrusion Detection System for Network Security

---

# Developed By

Shaik Tasneem
Master of Computer Applications (MCA)
Andhra University

---

# Project Guide

Mohammed Ashfakh
Web developer, Cloud & Cybersecurity Engineer

---

# Academic Year

2025 – 2026

---

# System Requirements

Operating System:
Ubuntu Linux (Virtual Machine)

Software Requirements:

Python 3
Flask
Pandas
Scikit-learn

Browser:
Chrome / Firefox

---

# Project Structure


intrusion-detection-project-ML
│
├── README.md
├── requirements.txt
│
├── dataset
│   ├── dataset.csv
│   ├── normal_traffic.csv
│   └── attack_traffic.csv
│
├── model
│   └── model.pkl
│
├── results
│   └── predictions.txt
│
├── src
│   ├── app.py
│   └── train_model.py
│
├── templates
│   ├── index.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── result.html
│   └── about.html
│
├── static
│   ├── style.css
│   └── logo.png
│
├── scripts
│   ├── install-libraries.sh
│   └── verify-installation.sh
│
└── website-theme
    └── theme-notes.txt


---

# Installation (Ubuntu)

Update system:


sudo apt update


Install required Python libraries:


sudo apt install python3-flask python3-pandas python3-sklearn -y


---

# Train the Machine Learning Model

Run:


python3 src/train_model.py


This will generate the trained model:


model/model.pkl


---

# Run the Web Application

Start the Flask server:


python3 src/app.py


---

# Open the Website

Open browser and visit:


http://localhost:5000


If running on VM server:


http://SERVER-IP:5000


---

# How the System Works

1. User uploads network traffic dataset
2. System reads the dataset
3. Machine learning model analyzes the data
4. Traffic is classified as **Normal** or **Attack**
5. Result is displayed on the website

---

# Features

Machine Learning based intrusion detection
Web-based user interface
Upload dataset for analysis
Dynamic cybersecurity dashboard
Detection of normal and malicious traffic

---

# Future Improvements

Real-time network packet monitoring
Graph-based attack visualization
Integration with real IDS datasets (NSL-KDD, CICIDS2017)
User authentication system
Database logging of detected attacks

---

# Conclusion

This project demonstrates how **Machine Learning techniques can enhance cybersecurity systems** by detecting abnormal network traffic and potential threats.

---

# License

This project is developed for **academic purposes as part of the MCA program at Andhra University**.

