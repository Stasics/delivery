from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import user_routes

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://project-delivery-roan.vercel.app/"],  # Адрес Live Server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)