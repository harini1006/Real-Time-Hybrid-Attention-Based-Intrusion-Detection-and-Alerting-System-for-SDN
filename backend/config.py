import os

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATASET_DIR = PROJECT_DIR
MODEL_DIR = os.path.join(BASE_DIR, "saved_model")

# === JWT Auth ===
SECRET_KEY = "ids-sdn-secret-key-2024-hybrid-attention"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Admin credentials (hardcoded for demo)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# === SMTP Email Settings ===
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "testharini10@gmail.com"  # Configure with real email
SMTP_PASS = "ggvh yipl flox qbob"  # Configure with app password
ALERT_RECIPIENT = "harinijuji@gmail.com"  # Admin email to receive alerts

# === Model Settings ===
SAMPLE_SIZE = 50000
BATCH_SIZE = 64
EPOCHS = 15
LEARNING_RATE = 0.001
HIDDEN_SIZE = 128
NUM_LAYERS = 2
REALTIME_DELAY = 0.3  # seconds between real-time predictions
