import os
import pytest
from datetime import timedelta
from httpx import AsyncClient
from typing import AsyncGenerator
from fastapi import FastAPI
from dotenv import load_dotenv
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.test import finalizer, initializer
from asgi_lifespan import LifespanManager
from typing import Dict

from api.security import create_access_token


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


# @pytest.fixture(scope="session", autouse=True)
# def init_db():
#     load_dotenv()
#     db_url = os.getenv("TEST_DB_URL")
#     initializer(["database.models"], db_url=db_url, app_label="models")
#     yield
#     finalizer()


@pytest.fixture(scope="module")
def app() -> FastAPI:
    return FastAPI(title="Typhoon Test")


@pytest.fixture(scope="module")
def token_headers() -> Dict[str, str]:
    access_token = create_access_token("TestUser123", timedelta(minutes=30))
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="module")
async def client(app: FastAPI):
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://localhost:8000/") as c:
            yield c


@pytest.fixture(scope="module")
async def init_db():
    load_dotenv()
    await register_tortoise(
        app,
        db_url=os.getenv("DB_URL"),
        modules={"models": ["database.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )
    try:
        yield
    finally:
        await app.state._db.close_connections()


# @pytest.fixture(scope="module")
# async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
#     async with AsyncClient(app=app, base_url="http://localhost:8000") as c:
#         yield c
