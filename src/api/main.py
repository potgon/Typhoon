from fastapi import APIRouter

from .routes import assets, models, queue, login, users

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(queue.router, prefix="/queue", tags=["queue"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
