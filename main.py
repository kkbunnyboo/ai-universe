from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.config import settings
from src.api.router import api_router

app = FastAPI(
    title="AI Universe",
    description="Build your own AI universe platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return JSONResponse({"message": "Welcome to AI Universe 🌌"})


@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy"})


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
