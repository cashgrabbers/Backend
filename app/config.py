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
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "pyamqp://guest@localhost//"
    SENTRY_DSN: str = "YOUR_SENTRY_DSN"
    MKDOCS_CONFIG_FILE: str = "mkdocs.yml"
    DOCKERFILE: str = "Dockerfile"
    KUBERNETES_CONFIG_FILE: str = "k8s_config.yml"
    FLOWER_PORT: int = 5555
    FLOWER_URL_PREFIX: str = "flower"
    FLOWER_BASIC_AUTH: str = "user:password"
    BUBBLE_APP_URL: str ="https://e-wallet-94178.bubbleapps.io/version-test/dashboard"

    # class Config:
    #     env_file = ".env"

settings = Settings()
