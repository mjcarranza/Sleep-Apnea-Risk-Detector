import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load dataset
df = pd.read_csv("assets/apnea-training-dataset.csv")

# Assure there is no missing data in the dataset
required_columns = ['Age', 'Gender', 'BMI', 'Nasal_Airflow', 'Snoring', 'Treatment_Required', 'Has_Apnea']
df = df.dropna(subset=required_columns)

# Define input and output features
input_features = ['Age', 'Gender', 'BMI', 'Nasal_Airflow', 'Snoring']
X = df[input_features]

# Model: Treatment_Required
y_treatment = df['Treatment_Required']
X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(X, y_treatment, test_size=0.2, random_state=42)

model_treatment = RandomForestClassifier(n_estimators=100, random_state=42)
model_treatment.fit(X_train_t, y_train_t)

y_pred_t = model_treatment.predict(X_test_t)

print("=== Evaluation: Treatment_Required ===")
print(f"Accuracy: {accuracy_score(y_test_t, y_pred_t):.4f}")
print("Classification Report:")
print(classification_report(y_test_t, y_pred_t))
print("Confussion Matrix:")
print(confusion_matrix(y_test_t, y_pred_t), "\n")

# Save trained model
#joblib.dump(model_treatment, "modelo_treatment_required_rf.pkl")
