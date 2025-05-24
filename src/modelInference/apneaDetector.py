import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report

# 1. Cargar el dataset
df = pd.read_csv('/home/mario/Downloads/apnea_Training- Dataset.csv')

# 2. Definir columnas de entrada y salida
input_cols = ['Age', 'Gender', 'BMI', 'Nasal_Airflow', 'Snoring']
output_targets = {
    'AHI': 'regression',
    'Diagnosis_of_SDB': 'classification',
    'Severity': 'classification',
    'Treatment_Required': 'classification',
    'Has_Apnea': 'classification'
}

# 3. Preprocesamiento: escalar entradas
X = df[input_cols].copy()
X['Snoring'] = X['Snoring'].astype(int)  # asegurar tipo entero

scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# 4. Dividir datos en entrenamiento y prueba
X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)

# 5. Entrenar un modelo RandomForest para cada salida
models = {}
for target, task in output_targets.items():
    y = df[target]
    y_train = y.loc[X_train.index]
    y_test = y.loc[X_test.index]

    if task == 'regression':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(f"{target} - MSE: {mean_squared_error(y_test, y_pred):.4f}")
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(f"{target} - Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(classification_report(y_test, y_pred))

    models[target] = model

# 6. Función para hacer predicciones con nuevos datos
def predecir_todo(nuevos_datos: dict):
    input_df = pd.DataFrame([nuevos_datos])
    input_df['Snoring'] = input_df['Snoring'].astype(int)
    input_scaled = scaler.transform(input_df)

    predicciones = {}
    for target, model in models.items():
        pred = model.predict(input_scaled)
        predicciones[target] = pred[0]

    return predicciones

# 7. Ejemplo de uso
ejemplo = {
    'Age': 70,
    'Gender': 1,
    'BMI': 39.93,
    'Nasal_Airflow': 0.54,
    'Snoring': True
}

resultados = predecir_todo(ejemplo)
print("\nPredicción para entrada personalizada:")
print(resultados)
