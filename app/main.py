from fastapi import FastAPI
from routers import router as api_router
from middlewares import setup_middlewares

from database import Base, engine

app = FastAPI()

setup_middlewares(app)

Base.metadata.create_all(bind=engine)

app.include_router(api_router)
