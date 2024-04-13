from fastapi import APIRouter

from .schemas import Asset, ModelType

router = APIRouter()

@router.get("/assets/")
def read_assets():
    pass

@router.get("/models/")
def read_models():
    pass

@router.post("/model-queue/")
def enqueue_model(asset: Asset, model_type: ModelType):
    pass


