import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv("/home/mario/Downloads/apnea_Training- Dataset.csv")

# Supongamos que df es tu DataFrame
ordinal_mapping = {
    'None': 0,
    'Mild': 1,
    'Moderate': 2,
    'Severe': 3
}

# Crear una nueva columna 'Has_Apnea' basada en 'Diagnosis_of_SDB'
# Por ejemplo, para la columna 'Severity'
df['Severity'] = df['Severity'].fillna(0)
df['Diagnosis_of_SDB'] = df['Diagnosis_of_SDB'].fillna(0)

df.to_csv("apnea_dataset_with_apnea_flag.csv", index=False)