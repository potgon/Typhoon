from abc import ABC, abstractmethod


class ModelBuilder(ABC):
    @abstractmethod
    def build_model(self):
        pass
