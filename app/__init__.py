from fastapi import FastAPI
from .routers import user_routes  # Импортируем user_routes

app = FastAPI()

app.include_router(user_routes.router, prefix="/users")