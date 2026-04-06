from fastapi import APIRouter

from src.api.routes import system, tools

api_router = APIRouter()

api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(tools.router, prefix="/tools", tags=["Tools"])
