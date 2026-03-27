"""
Hybrid LSTM+Attention-inspired model using sklearn.
Uses MLPClassifier with attention-weighted feature importance.
"""
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
import joblib


class AttentionFeatureWeighter:
    """
    Computes attention weights for features using gradient-based importance.
    Simulates the attention mechanism by learning feature importance scores.
    """
    def __init__(self):
        self.feature_weights = None
    
    def fit(self, X, y):
        """Compute feature importance using a gradient boosting model."""
        # Use a lightweight GBM to compute feature importance as attention weights
        gb = GradientBoostingClassifier(
            n_estimators=50, max_depth=4, random_state=42,
            subsample=0.8, learning_rate=0.1
        )
        gb.fit(X, y)
        # Normalize importances to [0, 1] as attention weights
        imp = gb.feature_importances_
        self.feature_weights = imp / (imp.max() + 1e-8)
        return self
    
    def transform(self, X):
        """Apply attention weights to features."""
        if self.feature_weights is None:
            return X
        return X * self.feature_weights
    
    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)


class HybridAttentionModel:
    """
    Hybrid model combining attention-weighted features with a deep MLP.
    Simulates LSTM+Attention architecture using sklearn components.
    """
    def __init__(self, hidden_layers=(256, 128, 64), max_iter=50, learning_rate=0.001):
        self.attention = AttentionFeatureWeighter()
        self.classifier = MLPClassifier(
            hidden_layer_sizes=hidden_layers,
            activation='relu',
            solver='adam',
            learning_rate_init=learning_rate,
            max_iter=max_iter,
            batch_size=256,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=10,
            random_state=42,
            verbose=True,
        )
    
    def fit(self, X, y):
        """Train the model: compute attention weights then train classifier."""
        print("  Computing attention weights...")
        X_weighted = self.attention.fit_transform(X, y)
        print(f"  Top 10 attention features: {np.argsort(self.attention.feature_weights)[-10:]}")
        print("  Training neural network classifier...")
        self.classifier.fit(X_weighted, y)
        return self
    
    def predict(self, X):
        """Predict class labels."""
        X_weighted = self.attention.transform(X)
        return self.classifier.predict(X_weighted)
    
    def predict_proba(self, X):
        """Predict class probabilities."""
        X_weighted = self.attention.transform(X)
        return self.classifier.predict_proba(X_weighted)
    
    def save(self, path):
        """Save model to disk."""
        joblib.dump({
            'attention': self.attention,
            'classifier': self.classifier,
        }, path)
        print(f"  Model saved to {path}")
    
    @classmethod
    def load(cls, path):
        """Load model from disk."""
        data = joblib.load(path)
        model = cls.__new__(cls)
        model.attention = data['attention']
        model.classifier = data['classifier']
        return model
