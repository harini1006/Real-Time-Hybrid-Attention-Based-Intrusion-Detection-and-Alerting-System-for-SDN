"""
Training script for the Hybrid Attention-Based IDS model.
Loads all CICIDS 2017 CSVs, preprocesses, trains, and saves the model.
"""
import os
import sys
import json
import time
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MODEL_DIR, SAMPLE_SIZE
from preprocessing import load_all_csvs, preprocess_dataframe, save_artifacts
from model import HybridAttentionModel


def train():
    print("=" * 60)
    print("  HYBRID ATTENTION-BASED IDS MODEL TRAINING")
    print("=" * 60)

    # Load data
    print("\n[1/5] Loading dataset...")
    df = load_all_csvs()

    # Preprocess
    print("\n[2/5] Preprocessing...")
    X, y, scaler, label_encoder, feature_names = preprocess_dataframe(
        df, fit_new=True, sample_size=SAMPLE_SIZE
    )
    num_classes = len(label_encoder.classes_)
    input_size = X.shape[1]

    print(f"  Input features: {input_size}")
    print(f"  Number of classes: {num_classes}")
    safe_classes = [c.encode('ascii', 'replace').decode() for c in label_encoder.classes_]
    print(f"  Classes: {safe_classes}")

    # Split
    unique, counts = np.unique(y, return_counts=True)
    min_count = counts.min()
    print(f"  Min class count: {min_count}")

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42,
            stratify=y if min_count >= 2 else None
        )
    except Exception:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    print(f"  Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Step 1: Compute attention weights on ORIGINAL data (fast — before SMOTE)
    print("\n[3/5] Computing attention weights...")
    from sklearn.ensemble import GradientBoostingClassifier
    gb = GradientBoostingClassifier(
        n_estimators=50, max_depth=4, random_state=42,
        subsample=0.8, learning_rate=0.1
    )
    gb.fit(X_train, y_train)
    attention_weights = gb.feature_importances_
    attention_weights = attention_weights / (attention_weights.max() + 1e-8)
    print(f"  Top 5 features: {np.argsort(attention_weights)[-5:][::-1]}")

    # Step 2: SMOTE oversampling to balance minority classes
    print("\n  Applying SMOTE oversampling...")
    from imblearn.over_sampling import SMOTE
    unique_train, counts_train = np.unique(y_train, return_counts=True)
    min_train = counts_train.min()
    max_per_class = 3000
    sampling_strategy = {}
    for cls, cnt in zip(unique_train, counts_train):
        sampling_strategy[cls] = max(cnt, min(max_per_class, cnt * 10))
    k = min(5, min_train - 1) if min_train > 1 else 1
    smote = SMOTE(random_state=42, k_neighbors=k, sampling_strategy=sampling_strategy)
    X_train, y_train = smote.fit_resample(X_train, y_train)
    unique_after, counts_after = np.unique(y_train, return_counts=True)
    print(f"  SMOTE applied! Train samples: {len(X_train):,}")
    print(f"  Class distribution after SMOTE: min={counts_after.min()}, max={counts_after.max()}")

    # Step 3: Apply attention weights and train MLP
    print("\n[4/5] Training MLP classifier...")
    X_train_weighted = X_train * attention_weights
    X_test_weighted = X_test * attention_weights

    from sklearn.neural_network import MLPClassifier
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation='relu',
        solver='adam',
        learning_rate_init=0.01,
        max_iter=15,
        batch_size=256,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=10,
        random_state=42,
        verbose=True,
    )

    start_time = time.time()
    mlp.fit(X_train_weighted, y_train)
    train_time = time.time() - start_time
    print(f"  Training completed in {train_time:.1f}s")

    # Build model object for saving
    from model import AttentionFeatureWeighter, HybridAttentionModel
    model = HybridAttentionModel.__new__(HybridAttentionModel)
    model.attention = AttentionFeatureWeighter()
    model.attention.feature_weights = attention_weights
    model.classifier = mlp

    # Evaluate
    print("\n[5/5] Evaluating...")
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

    # Save everything
    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save(os.path.join(MODEL_DIR, "model.pkl"))
    save_artifacts(scaler, label_encoder, feature_names)

    # Save metrics
    metrics = {
        "accuracy": float(round(accuracy, 4)),
        "precision": float(round(precision, 4)),
        "recall": float(round(recall, 4)),
        "f1_score": float(round(f1, 4)),
        "confusion_matrix": cm.tolist(),
        "class_names": list(label_encoder.classes_),
        "training_time_seconds": round(train_time, 1),
        "num_train_samples": len(X_train),
        "num_test_samples": len(X_test),
        "total_samples": len(X),
    }
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"\n  Model saved to {MODEL_DIR}")
    print("=" * 60)
    print("  TRAINING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    train()
