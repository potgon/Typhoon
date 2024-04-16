import os
import pytest
from tortoise.contrib.fastapi import register_tortoise
from httpx import AsyncClient
from fastapi import FastAPI
from dotenv import load_dotenv
from typing import Dict


from database.models import Asset
from api.tests.conftest import token_headers, client, app


# @pytest.mark.anyio
# async def test_read_asset(client: AsyncClient):
#     load_dotenv()
#     register_tortoise(
#         app,
#         db_url=os.getenv("DB_URL"),
#         modules={"models": ["database.models"]},
#         generate_schemas=False,
#         add_exception_handlers=True,
#     )
#     asset = await Asset.filter(id=1).first()
#     response = await client.get(f"/api/v1/assets/{asset.id}", headers=token_headers)
#     assert response.status_code == 200
#     content = response.json()

#     assert content["id"] == asset.id
#     assert content["ticker"] == asset.ticker
#     assert content["name"] == asset.name
#     assert content["asset_type"] == asset.asset_type
#     assert content["sector"] == asset.sector


@pytest.mark.asyncio
async def test_read_asset(
    client: AsyncClient, token_headers: Dict[str, str], app: FastAPI
) -> None:
    asset = await Asset.filter(id=1).first()
    response = await client.get(f"/api/v1/assets/{asset.id}", headers=token_headers)
    assert response.status_code == 200
    content = response.json()

    assert content["id"] == asset.id
    assert content["ticker"] == asset.ticker
    assert content["name"] == asset.name
    assert content["asset_type"] == asset.asset_type
    assert content["sector"] == asset.sector
