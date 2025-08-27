import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import joblib

# Cargar dataset y modelo
df = pd.read_csv("assets/posturesJointsDataset.csv")
clf = joblib.load("data/models/pose_classifier_rf.pkl")

# Features y labels
features = df.drop("label", axis=1).columns

# Importancia de cada feature individual
importances = clf.feature_importances_

# Crear DataFrame de importancia
feat_imp = pd.DataFrame({"feature": features, "importance": importances})
feat_imp = feat_imp.sort_values("importance", ascending=False)

print("📊 Top 15 features más importantes:")
print(feat_imp.head(15))

# Graficar top 15
plt.figure(figsize=(10,6))
plt.barh(feat_imp["feature"].head(15), feat_imp["importance"].head(15))
plt.gca().invert_yaxis()
plt.title("Top 15 features más importantes (Random Forest)")
plt.xlabel("Importancia")
plt.show()

# 🔹 Agrupar por joint (x,y,z,vis de cada landmark)
joint_importances = {}
for i in range(33):
    joint_feats = [f"x_{i}", f"y_{i}", f"z_{i}", f"vis_{i}"]
    joint_importances[f"joint_{i}"] = feat_imp[
        feat_imp["feature"].isin(joint_feats)
    ]["importance"].sum()

# Ordenar por importancia
joint_importances = dict(sorted(joint_importances.items(), key=lambda x: x[1], reverse=True))

print("\n📊 Importancia por joint:")
for joint, score in list(joint_importances.items())[:10]:
    print(f"{joint}: {score:.4f}")

# Graficar top 10 joints
plt.figure(figsize=(10,6))
plt.barh(list(joint_importances.keys())[:10], list(joint_importances.values())[:10])
plt.gca().invert_yaxis()
plt.title("Top 10 joints más importantes (Random Forest)")
plt.xlabel("Importancia acumulada (x,y,z,vis)")
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