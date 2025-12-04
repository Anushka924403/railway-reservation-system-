# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key_change_this")
    # Default to a local SQLite DB for easy local development. To use MySQL, set DATABASE_URI env var.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///railway.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
    # AI config placeholders
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")