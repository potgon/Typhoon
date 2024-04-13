from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from database.models import Asset, ModelType
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
        return [asset_queryset]
    raise HTTPException(status_code=500, detail="Server error: assets could not be retrieved")

@router.get("/models/", response_model=List[ModelTypeModel])
async def read_models(model_name: Optional[str] = Query(None)):
    if model_name:
        model = await ModelType.filter(model_name=model_name).first()
        if model is None:
            raise HTTPException(status_code=404, detail="Model type not found")
        return [model]
    model_queryset = await ModelType.all()
    if model_queryset:
        return [model_queryset]
    raise HTTPException(status_code=500, detail="Server error: model types could not be retrieved")

@router.post("/models/")
def train_model(asset: Asset, model_type: ModelTypeModel):
    pass

@router.get("/queue/")
def queue_position(user: UserModel):
    pass


