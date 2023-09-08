"""
config.py
"""

from pydantic_settings import BaseSettings
import base64
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./db.sqlite3"
    SECRET_KEY: str = "YOUR_SECRET_KEY"
    ORIGINS: str = "*"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000000
    PAYPAL_CLIENT_ID: str = os.environ.get('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET: str = os.environ.get('PAYPAL_CLIENT_SECRET')
    PAYPAL_API_KEY: str = base64.b64encode((PAYPAL_CLIENT_ID + ':' + PAYPAL_CLIENT_SECRET).encode('utf-8')).decode('utf-8')
    BUBBLE_APP_URL: str ="https://e-wallet-94178.bubbleapps.io/version-test/dashboard"

    # class Config:
    #     env_file = ".env"

settings = Settings()
