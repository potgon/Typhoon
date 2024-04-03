import os
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError
from typing import Optional, Dict, Type

from .model_base import ModelBuilder
from .lstm_model import LSTMModel
from database.models import ModelType
from utils.logger import make_log

MODEL_MAPPING = Dict[str, Type[ModelBuilder]] = {
    os.getenv("LSTM_MODEL_NAME"): LSTMModel,
}


class ModelFactory:
    @staticmethod
    async def get_built_model(model_type_id: int, **kwargs) -> Optional[ModelBuilder]:
        try:
            model_type = await ModelType.filter(id=model_type_id).first()
        except (DoesNotExist, IntegrityError, OperationalError) as e:
            make_log(
                "MODEL_BUILDER",
                40,
                "trainer_workflow.log",
                f"Error retrieving model_type from database: {str(e)}",
            )
            return None

        model_constructor = MODEL_MAPPING.get(model_type.model_name)
        if model_constructor:
            return model_constructor(**kwargs)
        else:
            make_log(
                "MODEL_BUILDER",
                40,
                "trainer_workflow.log",
                f"No model constructor found for model type: {model_type.model_name}",
            )
            return None
