from fastapi import APIRouter

from api.routes import assets, models, queue

api_router = APIRouter()
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(models.router, prefix="/models", tags=["models"])