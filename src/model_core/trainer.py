# import json
# import os
# import tensorflow as tf

# from ..database.models import TrainedModel, ModelType


# class Trainer:
#     def __init__(self):
#         self.val_performance = {}
#         self.performance = {}
#         self.priority_counter = 0
#         self.current_model_instance = None
#         self.current_trained_model = None

#     def enqueue_model(self, user, asset, model):
#         if user.priorityuser.priority:
#             self.prio_queue.append((user, asset, model))
#         else:
#             self.queue.append((user, asset, model))

#     def _get_next_tuple(self):
#         if self.prio_queue and self.priority_counter < 5:
#             self.priority_counter += 1
#             return self.prio_queue.pop()
#         else:
#             self.priority_counter = 0
#             return self.queue.pop()

#     def _compile_and_fit(model, window, epochs=20, patience=2):
#         early_stopping = tf.keras.callbacks.EarlyStopping(
#             monitor="val_loss", patience=patience, mode="min"
#         )
#         model.compile(
#             loss=tf.losses.MeanSquaredError(),
#             optimizer=tf.optimizers.Adam(),
#             metrics=[tf.metrics.MeanAbsoluteError()],
#         )
#         history = model.fit(
#             window.train,
#             epochs=epochs,
#             validation_data=window.val,
#             callbacks=[early_stopping],
#         )

#         return history

#     def train(self):
#         self.current_model_instance = self._get_next_tuple()[2]
#         self.current_trained_model = self._compile_and_fit(
#             self.current_model_instance.model, self.current_model_instance.window
#         )

#     def evaluate(self):
#         self.val_performance = self.current_trained_model.evaluate(
#             self.current_model_instance.window.val
#         )
#         self.performance = self.current_trained_model.evaluate(
#             self.current_model_instance.window.test, verbose=0
#         )

#     def predict(self):
#         pass

#     def save_model(self, signal):
#         model_str = self.current_model_instance.__str__()
#         self._save_new_model(model_str)
#         if signal:
#             serialized_model = self._serialize_model()
#             TrainedModel(
#                 name=model_str["model_name"],
#                 performance_metrics=json.dumps(self.performance),
#                 hyperparameters=model_str["default_hyperparameters"],
#                 model_architecture=model_str["default_model_architecture"],
#                 serialized_model=serialized_model,
#                 training_logs=json.dumps(self.val_performance),
#                 status="Inactive",
#             ).save()

#     def _serialize_model(self):
#         save_path = os.getenv("TRAINED_MODEL_SAVE_PATH")
#         self.current_trained_model.save(save_path)
#         with open(save_path, "rb") as file:
#             serialized_model = file.read()
#         os.remove(save_path)
#         return serialized_model

#     def _save_new_model(self, model_str):
#         if not ModelType.objects.filter(name=model_str["model_name"]).exists():
#             ModelType(
#                 name=model_str["model_name"],
#                 description=model_str["description"],
#                 default_hyperparameters=model_str["default_hyperparameters"],
#                 default_model_architecture=model_str["default_model_architecture"],
#             ).save()
