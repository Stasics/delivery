import uvicorn
from app import app # Импорт приложения
from app.core.config import settings
from app.models import Base, engine # Импорт engine

# app = create_app() # убрали, app уже инициализировано

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) #  Использовать await

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_db_and_tables())
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # reload=True для автоматического перезапуска при изменениях