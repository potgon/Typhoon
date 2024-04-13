from pydantic import BaseModel

class ModelTypeModel(BaseModel):
    id: int
    model_name: str
    description: str
    default_hyperparameters: str | None
    default_model_architecture: str | None
    
class AssetModel(BaseModel):
    id: int
    ticker: str
    name: str
    sector: str | None
    asset_type: str | None
    
    class Config:
        orm_mode=True
    
class UserModel(BaseModel):
    id: int
    username: str