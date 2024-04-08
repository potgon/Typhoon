import aiofiles
import json
import os
import tensorflow as tf
from keras.callbacks import History
from typing import Optional, ByteString
from tortoise.exceptions import BaseORMException

from .model_builders.model_factory import ModelFactory
from database.models import TrainedModel, ModelType, Queue  # , TempModel
from utils.logger import make_log


class Trainer:
    def __init__(self):
        self.val_performance = {}
        self.performance = {}
        self.current_request = None  # Queue Instance
        self.priority_counter = 0
        self.current_model_instance = None  # Model Builder Instance
        self.current_trained_model = None  # Keras Model

    async def _get_next_queue_item(
        self,
    ) -> Optional[Queue]:
        """Uses self.priority_counter to retrieve the next priority or non-priority item from the queue

        Returns:
            Optional[Queue]: Queue instance
        """
        if self.priority_counter < 5:
            queue_item = await Queue.filter(priority=1).order_by("created_at").first()
        else:
            queue_item = await Queue.filter(priority=0).order_by("created_at").first()

        if queue_item:
            self._manage_prio_counter(queue_item.priority)
            return queue_item
        else:
            make_log(
                "TRAINER",
                40,
                "trainer_workflow.log",
                f"Error retrieving query item: {queue_item}",
            )
            return None

    def _manage_prio_counter(self, queue_item_priority: int) -> None:
        """Keeps track of completed priority requests and manages self.priority_counter

        Args:
            queue_item_priority (int): Queue item instance priority field
        """
        if queue_item_priority == 1:
            self.priority_counter += 1
        else:
            self.priority_counter == 0

    def _compile_and_fit(model, window, epochs=20, patience=2) -> History:
        """Compiles and fits current model instance to given data window

        Args:
            model (ModelBase): Model builder instance
            window (WindowGenerator): Data window
            epochs (int, optional): _description_. Defaults to 20.
            patience (int, optional): _description_. Defaults to 2.

        Returns:
            History: Keras History object, records events
        """
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=patience, mode="min"
        )
        model.compile(
            loss=tf.losses.MeanSquaredError(),
            optimizer=tf.optimizers.Adam(),
            metrics=[tf.metrics.MeanAbsoluteError()],
        )
        history = model.fit(
            window.train,
            epochs=epochs,
            validation_data=window.val,
            callbacks=[early_stopping],
        )

        return history

    async def train(self) -> None:
        """Gets model type and asset from current request and trains it

        Raises:
            TypeError: Raised if no queue item could be retrieved
            TypeError: Raised if factory could not return any model instance
        """
        self.current_request = self._get_next_queue_item()
        if self.current_request is None:
            make_log(
                "TRAINER",
                40,
                "trainer_workflow.log",
                f"Cannot retrieve queue item",
            )
            raise TypeError  # Catch this in service module
        else:
            built_model = ModelFactory.get_built_model(
                self.current_request.model_type, self.current_request.asset
            )
            if not built_model:
                make_log(
                    "TRAINER",
                    40,
                    "trainer_workflow.log",
                    "Could not retrieve model instance from model factory",
                )
                raise TypeError  # Catch this in service module
            self.current_model_instance = built_model
            self.current_trained_model = self._compile_and_fit(
                self.current_model_instance.model, self.current_model_instance.window
            )

    def evaluate(self) -> None:
        """Stores performance metrics of current trained model"""
        self.val_performance = self.current_trained_model.evaluate(
            self.current_model_instance.window.val
        )
        self.performance = self.current_trained_model.evaluate(
            self.current_model_instance.window.test, verbose=0
        )

    async def save_model(self) -> Optional[TrainedModel]:
        """Saves current trained model to database

        Returns:
            Optional[TrainedModel]: TrainedModel instance
        """
        model_dict = self.current_model_instance.to_dict()
        self._save_new_model_type(model_dict)
        serialized_model = self._serialize_model()

        model = await TrainedModel.create(
            model_type=self.current_model_instance,
            asset=self.current_request.asset,
            user=self.current_request.user,
            model_name=model_dict["model_name"],
            performance_metrics=json.dumps(self.performance),
            hyperparameters=model_dict["default_hyperparameters"],
            model_architecture=model_dict["default_model_architecture"],
            serialized_model=serialized_model,
            training_logs=json.dumps(self.val_performance),
            status="Temporal",
        )
        if model is None:
            make_log(
                "TRAINER",
                40,
                "trainer_workflow.log",
                f"Error saving model",
            )
            return None
        return model

    # async def save_temp_model(self) -> Optional[TempModel]:
    #     model_dict = self.current_model_instance.to_dict()
    #     serialized_model = self._serialize_model()
    #     try:
    #         model = await TempModel.create(
    #             model_type = self.current_model_instance,
    #             asset = self.current_request.asset,
    #             user = self.current_request.user,
    #             model_name=model_dict["model_name"],
    #             performance_metrics=json.dumps(self.performance),
    #             hyperparameters=model_dict["default_hyperparameters"],
    #             model_architecture=model_dict["default_model_architecture"],
    #             serialized_model=serialized_model,
    #             training_logs=json.dumps(self.val_performance),
    #             status="Temporal",
    #         )
    #     except BaseORMException as e:
    #         make_log(
    #             "TRAINER",
    #             40,
    #             "trainer_workflow.log",
    #             f"Error saving temporal model: {str(e)}",
    #         )
    #         return None
    #     return model

    async def _serialize_model(self) -> ByteString:
        """Serializes current trained model

        Returns:
            ByteString: ByteString containing Binary serialized model
        """
        save_path = os.getenv("TRAINED_MODEL_SAVE_PATH")
        self.current_trained_model.save(save_path)
        async with aiofiles.open(save_path, "rb") as file:
            serialized_model = await file.read()
        os.remove(save_path)
        return serialized_model

    async def _save_new_model_type(self, model_dict) -> None:
        """Checks if model type of current trained model does not exist and creates it otherwise

        Args:
            model_dict (Dict): Dict with model instance info sent from save_temp_model

        Returns:
            None
        """
        model_type_exists = await ModelType.filter(
            model_name=model_dict["model_name"]
        ).exists()

        if not model_type_exists:
            new_model = await ModelType.create(
                name=model_dict["model_name"],
                description=model_dict["description"],
                default_hyperparameters=model_dict["default_hyperparameters"],
                default_model_architecture=model_dict["default_model_architecture"],
            )
            make_log(
                "TRAINER",
                20,
                "trainer_workflow.log",
                f"New model type stored: Is ModelType = {new_model} ?",
            )
        else:
            make_log(
                "TRAINER",
                20,
                "trainer_workflow.log",
                f"Nothing created. Is True  = {model_type_exists} ?",
            )
