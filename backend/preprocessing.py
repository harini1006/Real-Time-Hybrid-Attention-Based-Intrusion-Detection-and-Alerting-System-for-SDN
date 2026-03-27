import os
import glob
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
from config import DATASET_DIR, MODEL_DIR, SAMPLE_SIZE


def load_all_csvs(dataset_dir=None):
    """Load and concatenate all CICIDS 2017 CSV files."""
    if dataset_dir is None:
        dataset_dir = DATASET_DIR
    csv_files = glob.glob(os.path.join(dataset_dir, "*.csv"))
    print(f"Found {len(csv_files)} CSV files")
    dfs = []
    for f in csv_files:
        print(f"  Loading: {os.path.basename(f)}")
        df = pd.read_csv(f, low_memory=False)
        df.columns = df.columns.str.strip()
        dfs.append(df)
    combined = pd.concat(dfs, ignore_index=True)
    print(f"Combined dataset shape: {combined.shape}")
    return combined


def preprocess_dataframe(df, fit_new=True, scaler=None, label_encoder=None, sample_size=None):
    """
    Full preprocessing pipeline for CICIDS 2017 dataset.
    Returns: X (scaled features), y (encoded labels), scaler, label_encoder, feature_names
    """
    # Columns already stripped in load_all_csvs

    # Replace infinite values
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Drop rows with NaN
    df.dropna(inplace=True)

    # Sample if needed
    if sample_size and len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)
        print(f"Sampled to {sample_size} rows")

    # Separate label (optional during prediction)
    y = None
    if "Label" in df.columns:
        labels = df["Label"].copy()
        features = df.drop(columns=["Label"])
    else:
        labels = None
        features = df.copy()

    # Keep only numeric columns
    features = features.select_dtypes(include=[np.number])
    feature_names = features.columns.tolist()

    # Encode labels (only during training)
    if fit_new:
        if labels is None:
            raise ValueError("'Label' column required for training")
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(labels)
    elif labels is not None and label_encoder is not None:
        # During prediction, encode known labels and skip unknown ones
        known_labels = set(label_encoder.classes_)
        y = []
        for lbl in labels:
            if lbl in known_labels:
                y.append(label_encoder.transform([lbl])[0])
            else:
                y.append(-1)  # Mark unseen labels as -1
        y = np.array(y)

    # Scale features
    X = features.values.astype(np.float32)
    if fit_new:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
    else:
        X = scaler.transform(X)

    X = X.astype(np.float32)

    print(f"Features shape: {X.shape}, Classes: {len(np.unique(y))}")
    print(f"Label classes: {list(label_encoder.classes_)}")

    return X, y, scaler, label_encoder, feature_names


def save_artifacts(scaler, label_encoder, feature_names):
    """Save preprocessing artifacts."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    joblib.dump(label_encoder, os.path.join(MODEL_DIR, "label_encoder.pkl"))
    joblib.dump(feature_names, os.path.join(MODEL_DIR, "feature_names.pkl"))
    print("Preprocessing artifacts saved.")


def load_artifacts():
    """Load saved preprocessing artifacts."""
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))
    feature_names = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
    return scaler, label_encoder, feature_names


def preprocess_single_row(row_dict, scaler, feature_names):
    """Preprocess a single row for prediction."""
    row_df = pd.DataFrame([row_dict])
    row_df.columns = row_df.columns.str.strip()

    # Keep only known numeric features
    row_features = []
    for fname in feature_names:
        if fname in row_df.columns:
            val = pd.to_numeric(row_df[fname].iloc[0], errors="coerce")
            row_features.append(0.0 if np.isnan(val) or np.isinf(val) else float(val))
        else:
            row_features.append(0.0)

    X = np.array([row_features], dtype=np.float32)
    X = scaler.transform(X)
    return X.astype(np.float32)
