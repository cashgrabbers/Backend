"""
config.py
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./db.sqlite3"
    SECRET_KEY: str = "YOUR_SECRET_KEY"
    ORIGINS: str = "*"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000000
    STRIPE_API_KEY: str = "YOUR_STRIPE_API_KEY"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "pyamqp://guest@localhost//"
    SENTRY_DSN: str = "YOUR_SENTRY_DSN"
    MKDOCS_CONFIG_FILE: str = "mkdocs.yml"
    DOCKERFILE: str = "Dockerfile"
    KUBERNETES_CONFIG_FILE: str = "k8s_config.yml"
    FLOWER_PORT: int = 5555
    FLOWER_URL_PREFIX: str = "flower"
    FLOWER_BASIC_AUTH: str = "user:password"

    class Config:
        env_file = ".env"

settings = Settings()
