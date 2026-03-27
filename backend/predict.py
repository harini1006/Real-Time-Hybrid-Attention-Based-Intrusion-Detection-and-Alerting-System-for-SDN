"""Prediction engine - loads trained model and provides inference."""
import os
import numpy as np

from config import MODEL_DIR
from model import HybridAttentionModel
from preprocessing import load_artifacts, preprocess_single_row


class PredictionEngine:
    """Loads the trained model and runs predictions."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self._loaded = False

    def load(self):
        """Load model and preprocessing artifacts."""
        model_path = os.path.join(MODEL_DIR, "model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                "Trained model not found. Run train.py first."
            )
        self.model = HybridAttentionModel.load(model_path)
        self.scaler, self.label_encoder, self.feature_names = load_artifacts()
        self._loaded = True
        print("Prediction engine loaded successfully.")

    @property
    def is_loaded(self):
        return self._loaded

    def predict_batch(self, X: np.ndarray):
        """
        Predict on a batch of preprocessed features.
        Returns list of dicts with label, confidence.
        """
        if not self._loaded:
            self.load()

        probs = self.model.predict_proba(X)
        predicted = probs.argmax(axis=1)
        confidences = probs.max(axis=1)

        results = []
        for i in range(len(predicted)):
            label_idx = predicted[i]
            label = self.label_encoder.classes_[label_idx]
            conf = confidences[i]
            results.append({
                "prediction": label,
                "attack_type": label if label != "BENIGN" else "None",
                "confidence": round(float(conf) * 100, 2),
                "is_attack": label != "BENIGN",
            })
        return results

    def predict_single(self, row_dict: dict):
        """Predict a single row from raw feature dict."""
        if not self._loaded:
            self.load()

        X = preprocess_single_row(row_dict, self.scaler, self.feature_names)
        results = self.predict_batch(X)
        return results[0]
