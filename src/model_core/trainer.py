import json
import os
import tensorflow as tf
from typing import Optional
from tortoise.exceptions import BaseORMException

from .model_builders.model_factory import ModelFactory
from database.models import TrainedModel, ModelType, Queue
from utils.logger import make_log


class Trainer:
    def __init__(self):
        self.val_performance = {}
        self.performance = {}
        self.priority_counter = 0
        self.current_model_instance = None
        self.current_trained_model = None

    async def _get_next_queue_item(
        self,
    ) -> Optional[Queue]:  # If return is None: continue
        try:
            if self.priority_counter < 5:
                queue_item = (
                    await Queue.filter(priority=1).order_by("created_at").first()
                )
            else:
                queue_item = (
                    await Queue.filter(priority=0).order_by("created_at").first()
                )
        except BaseORMException as e:
            make_log(
                "TRAINER",
                40,
                "trainer_workflow.log",
                f"Error retrieve queue item: {str(e)}",
            )
            return None
        if queue_item:
            self._reset_prio_counter(queue_item)
            return queue_item

    def _reset_prio_counter(self, queue_item: Queue):
        if queue_item.priority == 1:
            self.priority_counter += 1
        else:
            self.priority_counter == 0

    def _compile_and_fit(model, window, epochs=20, patience=2):
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

    def train(self):
        # Retrieve asset and user for later use
        queue = self._get_next_queue_item()
        if queue:
            built_model = ModelFactory.get_built_model(queue.model_type_id)
        else:
            make_log(
                "TRAINER", 40, "trainer_workflow.log", "Cannot retrieve queue item"
            )
            raise TypeError  # Catch this in service module
        if not built_model:
            raise TypeError  # Catch this in service module
        self.current_model_instance = built_model
        self.current_trained_model = self._compile_and_fit(
            self.current_model_instance.model, self.current_model_instance.window
        )

    def evaluate(self):
        self.val_performance = self.current_trained_model.evaluate(
            self.current_model_instance.window.val
        )
        self.performance = self.current_trained_model.evaluate(
            self.current_model_instance.window.test, verbose=0
        )

    def predict(self):
        pass

    def save_model(self, signal):
        model_str = self.current_model_instance.__str__()
        self._save_new_model(model_str)
        if signal:
            serialized_model = self._serialize_model()
            TrainedModel(
                name=model_str["model_name"],
                performance_metrics=json.dumps(self.performance),
                hyperparameters=model_str["default_hyperparameters"],
                model_architecture=model_str["default_model_architecture"],
                serialized_model=serialized_model,
                training_logs=json.dumps(self.val_performance),
                status="Inactive",
            ).save()

    def _serialize_model(self):
        save_path = os.getenv("TRAINED_MODEL_SAVE_PATH")
        self.current_trained_model.save(save_path)
        with open(save_path, "rb") as file:
            serialized_model = file.read()
        os.remove(save_path)
        return serialized_model

    async def _save_new_model(self, model_str) -> Optional[ModelType]:
        try:
            model_type_exists = await ModelType.filter(
                model_name=model_str["model_name"]
            ).exists()
        except BaseORMException as e:
            make_log(
                "TRAINER",
                40,
                "trainer_workflow.log",
                f"Error saving new model: {str(e)}",
            )
            return None
        if not model_type_exists:
            new_model = await ModelType.create(
                name=model_str["model_name"],
                description=model_str["description"],
                default_hyperparameters=model_str["default_hyperparameters"],
                default_model_architecture=model_str["default_model_architecture"],
            )
            return new_model
