import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mein-geheimer-fallback")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///default.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
