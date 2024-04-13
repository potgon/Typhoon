from fastapi import APIRouter, HTTPException
from typing import List

from database.models import Asset
from api.schemas import AssetModel

router = APIRouter()

@router.get("/", response_model=List[AssetModel])
async def read_all_assets():
    asset_queryset = await Asset.all()
    if asset_queryset is None:
        raise HTTPException(status_code=500, detail="Server error: assets could not be retrieved")
    return asset_queryset

@router.post("/{ticker}", response_model=AssetModel)
async def read_asset(ticker: str):
    asset = await Asset.filter(ticker=ticker).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
