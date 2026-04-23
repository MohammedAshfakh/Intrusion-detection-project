import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("📊 Loading dataset...")

# ---------------- BASE PATH ----------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
dataset_path = os.path.join(BASE_DIR, "dataset", "dataset.csv")

# ---------------- LOAD DATA ----------------
data = pd.read_csv(dataset_path)

print("✅ Dataset loaded")

# ---------------- PREPROCESS ----------------
# last column = label
X = data.iloc[:, :-1]
y = data.iloc[:, -1]

# convert label
y = y.apply(lambda x: 0 if x == 'normal' else 1)

# ---------------- SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------- TRAIN ----------------
print("🧠 Training model...")

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# ---------------- EVALUATE ----------------
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"📈 Accuracy: {accuracy:.2f}")

# ---------------- SAVE MODEL ----------------
model_dir = os.path.join(BASE_DIR, "model")

# create folder if not exists
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "model.pkl")

joblib.dump(model, model_path)

print(f"💾 Model saved at: {model_path}")
