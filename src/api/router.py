from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional

from database.models import Asset
from .schemas import AssetModel, ModelTypeModel, UserModel

router = APIRouter()

@router.get("/assets/", response_model=List[AssetModel])
async def read_assets(ticker: Optional[str] = Query(None)):
    if ticker:
        asset = await Asset.filter(ticker=ticker).first()
        if asset is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        return [asset]
    asset_queryset = await Asset.all()
    if asset_queryset:
        return JSONResponse(status_code=200, content={"Asset list: ": asset_queryset})
    raise HTTPException(status_code=500, detail="Server error: assets could not be retrieved")

@router.get("/models/")
def read_models():
    pass

@router.post("/models/")
def train_model(asset: Asset, model_type: ModelTypeModel):
    pass

@router.get("/queue/")
def queue_position(user: UserModel):
    pass


