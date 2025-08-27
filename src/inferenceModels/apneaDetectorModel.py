import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer, f1_score
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import accuracy_score
import joblib

# Load balanced dataset
df = pd.read_csv("assets/apnea-balanced-sobre.csv")

# Define features and labels
features = ['Age', 'Gender', 'BMI', 'Nasal_Airflow', 'Snoring']
target = 'Has_Apnea'
X = df[features]
y = df[target]

# Define base model
rf = RandomForestClassifier(random_state=42)

# Looking for the best parameters
param_dist = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [None, 5, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}

# Define random search
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_dist,
    n_iter=30,
    cv=5,
    scoring=make_scorer(f1_score),
    random_state=42,
    n_jobs=-1,
    verbose=1
)

# Execute search
random_search.fit(X, y)

# Print best parameters
print("=== Best hiperparams ===")
print(random_search.best_params_)

# Evaluate the optimized model with cossed validation
model_apnea = random_search.best_estimator_
f1_scores = cross_val_score(model_apnea, X, y, cv=5, scoring=make_scorer(f1_score))

print("\n=== Best model evaluation ===")
print(f"Mean F1-score (5-fold): {f1_scores.mean():.4f}")

y_pred = model_apnea.predict(X)
print(confusion_matrix(y, y_pred))
print(classification_report(y, y_pred))
acc = accuracy_score(y, y_pred)
print(f"Accuracy: {acc:.4f}")

#joblib.dump(model_apnea, "apnea-prediction-model.pkl")
