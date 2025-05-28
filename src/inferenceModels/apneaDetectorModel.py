import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer, f1_score
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import accuracy_score
import joblib

# Cargar el dataset balanceado
df = pd.read_csv("/home/mario/Downloads/apnea-balanced-sobre.csv")

# Definir características y etiqueta
features = ['Age', 'Gender', 'BMI', 'Nasal_Airflow', 'Snoring']
target = 'Has_Apnea'
X = df[features]
y = df[target]

# Definir el modelo base
rf = RandomForestClassifier(random_state=42)

# Espacio de búsqueda de hiperparámetros
param_dist = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [None, 5, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}

# Definir la búsqueda aleatoria
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

# Ejecutar búsqueda
random_search.fit(X, y)

# Mostrar los mejores parámetros
print("=== Mejores hiperparámetros encontrados ===")
print(random_search.best_params_)

# Evaluar el modelo optimizado con validación cruzada
model_apnea = random_search.best_estimator_
f1_scores = cross_val_score(model_apnea, X, y, cv=5, scoring=make_scorer(f1_score))

print("\n=== Evaluación con mejor modelo ===")
print(f"F1-score promedio (5-fold): {f1_scores.mean():.4f}")

y_pred = model_apnea.predict(X)
print(confusion_matrix(y, y_pred))
print(classification_report(y, y_pred))
acc = accuracy_score(y, y_pred)
print(f"Accuracy: {acc:.4f}")

joblib.dump(model_apnea, "apnea-prediction-model.pkl")

'''


# ---- FUNCIONES PARA PREDICCIÓN ----
def completar_dataset(csv_path, output_path):
    df_nuevo = pd.read_csv(csv_path)
    X_input = df_nuevo[input_features]

    # Cargar modelos
    model_airflow = joblib.load("modelo_nasal_airflow.pkl")
    model_treat = joblib.load("modelo_treatment_required.pkl")
    model_snore = joblib.load("modelo_snore.pkl")

    # Predecir columnas faltantes
    df_nuevo['Nasal_Airflow'] = model_airflow.predict(X_input)
    df_nuevo['Treatment_Required'] = model_treat.predict(X_input)
    df_nuevo['Snoring'] = model_snore.predict(X_input)

    # Guardar dataset enriquecido
    df_nuevo.to_csv(output_path, index=False)
    print(f"Archivo guardado en: {output_path}")

# Ejemplo de uso
completar_dataset("/home/mario/Downloads/processed.csv", "salida_completa.csv")


'''