from abc import ABC, abstractmethod


class ModelTrainer(ABC):
    @abstractmethod
    def train(self, data):
        pass

    @abstractmethod
    def evaluate(self, data):
        pass

    @abstractmethod
    def predict(self, data):
        pass
