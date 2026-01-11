import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'velib.db')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 heure