from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import user_routes

app = FastAPI()

# Настройка CORS
origins = [
    "https://project-delivery-roan.vercel.app",  # Replace with your Vercel frontend URL
]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(user_routes.router)