"""
This is the code used for training the sleep pose prediction model
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import joblib

# Load dataset
df = pd.read_csv("assets/posturesJointsDataset.csv")

# Divide features (x,y,z,vis) and labels (label)
X = df.drop("label", axis=1).values
y = df["label"].values

# Calculate class weights to balance dataset
classes = np.unique(y)
class_weights = compute_class_weight(class_weight="balanced", classes=classes, y=y)
class_weight_dict = {cls: w for cls, w in zip(classes, class_weights)}
print("[INFO] Class Weights:", class_weight_dict)

# Divide train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Train Random Forest
clf = RandomForestClassifier(
    n_estimators=200,          # more trees = best prediction model
    max_depth=None,
    class_weight=class_weight_dict,  # classes' balance
    random_state=42,
    n_jobs=-1                  # use all available cores
)
clf.fit(X_train, y_train)

# Model evaluation
y_pred = clf.predict(X_test)

print("\n📊 Clasification report:")
print(classification_report(y_test, y_pred))

print("\n📉 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save the trained model
joblib.dump(clf, "pose_classifier_rf.pkl")