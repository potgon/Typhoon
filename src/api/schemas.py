from pydantic import BaseModel

class ModelType(BaseModel):
    id: int
    model_name: str
    
class Asset(BaseModel):
    id: int
    ticker: str
    name: str
    
class User(BaseModel):
    id: int
    username: str