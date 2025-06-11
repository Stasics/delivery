from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import user_routes

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # URL вашего фронтенда
    allow_methods=["*"],  # Разрешить все методы (GET, POST, OPTIONS и т. д.)
    allow_headers=["*"],  # Разрешить все заголовки
    allow_credentials=True,  # Если используются куки или авторизация
)

app.include_router(user_routes.router)