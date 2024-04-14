from pydantic import BaseModel

class ModelTypeModel(BaseModel):
    id: int
    model_name: str
    description: str
    default_hyperparameters: str | None
    default_model_architecture: str | None

    class Config:
        orm_mode=True
            
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
    
    class Config:
        orm_mode=True
    
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class QueueModel(BaseModel):
    id: int
    user: str
    asset: str
    model_type: str
    
    class Config:
        orm_mode=True
        
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"