from fastapi import APIRouter, HTTPException
from typing import List

from database.models import ModelType
from api.schemas import ModelTypeModel

router = APIRouter()

@router.get("/", response_model=ModelTypeModel)
async def read_all_models():
    model_queryset = await ModelType.all()
    if model_queryset is None:
        raise HTTPException(status_code=500, detail="Server error: model types could not be retrieved")
    return model_queryset

@router.get("/{model_name}", response_model=List[ModelTypeModel])
async def read_model(model_name: str):
    model = await ModelType.filter(model_name=model_name).first()
    if model is None:
        raise HTTPException(status_code=404, detail="Model type not found")
    return model
