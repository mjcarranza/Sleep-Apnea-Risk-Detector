"""
This is the code used to get a report of the the main features that the model uses for its predictions
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import joblib

# Load model and image dataset
df = pd.read_csv("assets/posturesJointsDataset.csv")
clf = joblib.load("data/models/pose_classifier_rf.pkl")

# Features and labels
features = df.drop("label", axis=1).columns

# Importance of every single feature according to the AI model
importances = clf.feature_importances_

# Create importance features dataframe
feat_imp = pd.DataFrame({"feature": features, "importance": importances})
feat_imp = feat_imp.sort_values("importance", ascending=False)

print("Top 15 features more relevant:")
print(feat_imp.head(15))

# Graph top 15
plt.figure(figsize=(10,6))
plt.barh(feat_imp["feature"].head(15), feat_imp["importance"].head(15))
plt.gca().invert_yaxis()
plt.title("Top 15 features more relevant (Random Forest)")
plt.xlabel("Importance")
plt.show()

# Group per joint (x,y,z,vis of each landmark)
joint_importances = {}
for i in range(33):
    joint_feats = [f"x_{i}", f"y_{i}", f"z_{i}", f"vis_{i}"]
    joint_importances[f"joint_{i}"] = feat_imp[
        feat_imp["feature"].isin(joint_feats)
    ]["importance"].sum()

# Order per relevance
joint_importances = dict(sorted(joint_importances.items(), key=lambda x: x[1], reverse=True))

print("\nImportance per joint:")
for joint, score in list(joint_importances.items())[:10]:
    print(f"{joint}: {score:.4f}")

# Graph top 10 joints
plt.figure(figsize=(10,6))
plt.barh(list(joint_importances.keys())[:10], list(joint_importances.values())[:10])
plt.gca().invert_yaxis()
plt.title("Top 10 joints more relevant (Random Forest)")
plt.xlabel("Acumulated importance (x,y,z,vis)")
plt.show()






########----------------------- Sobre el grafico de 15 mas importantes ------------------########

## ANOTACIONES DE LO QUE VEMOS EN LAS GRAFICAS

'''
Los features más importantes según tu Random Forest son:

z_25, z_23, z_26, z_24 → profundidades de joints cercanos a pies y tobillos.

z_12, z_11 → profundidades de hombros/codos.

vis_11, vis_13, vis_25, vis_12, vis_29 → visibilidad de algunos puntos clave.

y_24, y_23 → coordenadas verticales de tobillos/piernas.

👉 Esto tiene sentido:

Para diferenciar supine vs prone (boca arriba vs boca abajo) → la profundidad (z) de hombros y cadera pesa mucho.

Para separar lateral vs fetal → las piernas (rodillas, tobillos) son decisivas, ya que en fetal están más flexionadas.

La visibilidad también ayuda (ej: en lateral una mano o pierna puede ocultarse, y eso es un indicio de postura).

📌 Conclusión

Tu modelo realmente está aprendiendo la lógica biomecánica correcta:

Tronco y hombros → distinguen arriba/abajo.

Piernas y rodillas → distinguen lateral vs fetal.

Visibilidad de extremidades → ayuda en casos de oclusión.

'''

# MAPA DEL CUERPO HUMANO SIMPLIFICADO (ver en assets)

'''
Aquí lo tienes 🎯: un mapa de cuerpo humano simplificado donde marqué en rojo los joints que tu Random Forest considera más importantes para clasificar posturas.

🔎 Interpretación

Hombros (L/R Shoulder) → claves para distinguir supino vs prono.

Caderas (L/R Hip) → determinan si el torso está girado.

Rodillas (L/R Knee) → muy relevantes para fetal vs lateral.

Talón izquierdo (L_Heel) → da pistas de la flexión en fetal.

👉 En otras palabras: tu modelo está usando justo las partes del cuerpo que intuitivamente diferencian las posiciones al dormir.
'''





########----------------------- Sobre el grafico de 10 Importancia Acumulada ------------------########