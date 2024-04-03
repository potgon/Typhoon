import tensorflow as tf
import json

from .model_base import ModelBuilder
from ..window_pipeline import data_processing


class LSTMModel(ModelBuilder):
    def __init__(self, units=50):
        self.window = data_processing("data\datasets\SP500_data.csv")
        self.units = units
        self.model = self.build_model()

    def build_model(self):
        self.model = tf.keras.Sequential(
            [
                tf.keras.layers.LSTM(self.units, return_sequences=False),
                tf.keras.layers.Dense(1),
            ]
        )

        self.model.compile(optimizer="adam", loss="mse")

    def __str__(self):
        default_hyperparameters = {"units": self.units}
        description = """
        The Long Short-Term Memory (LSTM) model is a type of recurrent neural network (RNN) designed to capture long-term dependencies in sequential data. Unlike traditional RNNs, LSTM networks are equipped with memory cells that can maintain information over extended time intervals, allowing them to effectively learn and remember patterns in time series, text, and other sequential data
        """
        return {
            "model_name": "LSTM",
            "description": description,
            "default_hyperparameters": json.dumps(default_hyperparameters),
            "default_model_architecture": "Layers: LSTM, Dense(1)",
        }
