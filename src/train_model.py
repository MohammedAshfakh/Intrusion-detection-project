import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

print("Loading dataset...")

# Load dataset
data = pd.read_csv("dataset/dataset.csv")

print("Dataset loaded successfully")

# Split features and label
X = data.drop("label", axis=1)
y = data["label"]

print("Training machine learning model...")

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

print("Model training completed")

# Save model
with open("model/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved successfully in model/model.pkl")
