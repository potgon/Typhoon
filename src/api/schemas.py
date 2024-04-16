from pydantic import BaseModel, ConfigDict


class ModelTypeModel(BaseModel):
    id: int
    model_name: str
    description: str
    default_hyperparameters: str
    default_model_architecture: str
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class AssetModel(BaseModel):
    id: int
    ticker: str
    name: str
    sector: str
    asset_type: str
    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
