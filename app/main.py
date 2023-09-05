from fastapi import FastAPI
from app.routers.routers import router as api_router
from app.routers.withdraws import router as withdraw_router
from app.routers.deposits import router as deposit_router
from app.middlewares import setup_middlewares

from app.database import Base, engine

app = FastAPI()

setup_middlewares(app)

Base.metadata.create_all(bind=engine)

app.include_router(api_router)
app.include_router(withdraw_router)
app.include_router(deposit_router)