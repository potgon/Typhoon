from fastapi import APIRouter

from .schemas import Asset, ModelType, User

router = APIRouter()

@router.get("/assets/")
def read_assets():
    pass

@router.get("/models/")
def read_models():
    pass

@router.post("/models/")
def train_model(asset: Asset, model_type: ModelType):
    pass

@router.get("/queue/")
def queue_position(user: User):
    pass


