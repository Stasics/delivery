from fastapi import FastAPI
from app.routers.user_routes import router as user_router

import uvicorn
import os

app = FastAPI()
app.include_router(user_router)


@app.get("/")  # <--- This defines a route for the root path (/)
async def read_root():
    return {"message": "Hello, World! from FastAPI on Render"} # or a JSON message

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)