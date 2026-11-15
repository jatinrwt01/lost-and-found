import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "smart-lost-found-dev-secret-key-2026")
    DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "lost_and_found.db"))
    # MOCK_MODE toggle: Set to True during early frontend/route development
    MOCK_MODE = os.environ.get("MOCK_MODE", "True").lower() in ("true", "1", "yes")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
