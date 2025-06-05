import uvicorn
from app.core.config import settings
import os  # Import the 'os' module

# from app import app # Убрали, так как теперь используем import string
# from app.models import Base, engine # Импорт engine

# app = create_app() # убрали, app уже инициализировано

# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    # import asyncio
    # asyncio.run(create_db_and_tables())

    # Use Render's PORT environment variable, or default to 8000 if not set
    port = int(os.environ.get("PORT", 8000))  # <----  IMPORTANT

    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)  # <----  Use the variable 'port' and include reload as you wish