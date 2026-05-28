import os
from dotenv import load_dotenv

# ==========================================
# RUTAS DEL SISTEMA
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
YOLO_WEIGHTS_PATH = os.path.join(DATA_DIR, "models", "best.pt")

# ==========================================
# BASE DE DATOS (Azure PostgreSQL)
# ==========================================
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ==========================================
# REGLAS DE NEGOCIO E IA
# ==========================================
YOLO_CONFIDENCE = 0.15
MAX_SEARCH_RESULTS = 3