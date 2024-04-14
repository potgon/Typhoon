from pydantic import BaseModel


class ModelTypeModel(BaseModel):
    id: int
    model_name: str
    description: str
    default_hyperparameters: str
    default_model_architecture: str

    class Config:
        from_attributes = True


class AssetModel(BaseModel):
    id: int
    ticker: str
    name: str
    sector: str
    asset_type: str

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
