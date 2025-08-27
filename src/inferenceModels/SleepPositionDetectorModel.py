import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import joblib

# Cargar dataset
df = pd.read_csv("assets/posturesJointsDataset.csv")

# Separar features (x,y,z,vis) y etiquetas (label)
X = df.drop("label", axis=1).values
y = df["label"].values

# Calcular class weights para balancear (opcional pero recomendado)
classes = np.unique(y)
class_weights = compute_class_weight(class_weight="balanced", classes=classes, y=y)
class_weight_dict = {cls: w for cls, w in zip(classes, class_weights)}
print("[INFO] Class Weights:", class_weight_dict)

# Dividir en train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Entrenar Random Forest
clf = RandomForestClassifier(
    n_estimators=200,          # más árboles = más robusto
    max_depth=None,            # dejar que crezca hasta converger
    class_weight=class_weight_dict,  # balancear clases
    random_state=42,
    n_jobs=-1                  # usa todos los cores disponibles
)
clf.fit(X_train, y_train)

# Evaluar
y_pred = clf.predict(X_test)

print("\n📊 Reporte de clasificación:")
print(classification_report(y_test, y_pred))

print("\n📉 Matriz de confusión:")
print(confusion_matrix(y_test, y_pred))


joblib.dump(clf, "pose_classifier_rf.pkl")