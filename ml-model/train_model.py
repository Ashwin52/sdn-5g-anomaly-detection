#!/usr/bin/env python3
"""
train_model.py (v2 - leakage-corrected)

Loads flow_stats.csv and labels rows using KNOWN TIME WINDOWS when attack
traffic was run (not derived from a feature used in training - avoids
label leakage).

You must fill in ATTACK_WINDOWS below with the actual timestamp range(s)
during which you ran attack_traffic.py.

Usage: python3 train_model.py /path/to/flow_stats.csv
"""

import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# ---- FILL THIS IN based on your actual attack run timestamps ----
ATTACK_WINDOWS = [
    (1784202802.5, 1784202812.7),  # adjust to match your actual attack run
]
# -------------------------------------------------------------------


def label_by_time_window(ts):
    for start, end in ATTACK_WINDOWS:
        if start <= ts <= end:
            return 1  # attack
    return 0  # normal


def load_and_prepare(csv_path):
    df = pd.read_csv(csv_path)
    df = df.sort_values(by=["src_mac", "dst_mac", "timestamp"]).reset_index(drop=True)

    df["inter_arrival"] = df.groupby(["src_mac", "dst_mac"])["timestamp"].diff()
    df["inter_arrival"] = df["inter_arrival"].fillna(df["inter_arrival"].median())

    df["avg_packet_size"] = df["byte_count"] / df["packet_count"]

    df["label"] = df["timestamp"].apply(label_by_time_window)

    return df


def train(df):
    features = ["packet_count", "byte_count", "avg_packet_size", "inter_arrival"]
    X = df[features]
    y = df["label"]

    print(f"Total samples: {len(df)}")
    print(f"Normal: {(y == 0).sum()}  |  Attack: {(y == 1).sum()}")

    if y.nunique() < 2:
        print("\nERROR: Only one class present after labeling.")
        print("Check that ATTACK_WINDOWS matches your actual attack run timestamps.")
        sys.exit(1)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    print("\n--- Evaluation ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Attack"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nFeature Importances:")
    for feat, imp in sorted(zip(features, clf.feature_importances_), key=lambda x: -x[1]):
        print(f"  {feat}: {imp:.4f}")

    return clf


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 train_model.py /path/to/flow_stats.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    df = load_and_prepare(csv_path)
    model = train(df)

    model_path = "anomaly_model.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")
