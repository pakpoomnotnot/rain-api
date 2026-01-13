from fastapi import FastAPI
from app.routers import rain

app = FastAPI()

app.include_router(rain.router)
