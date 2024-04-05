from abc import ABC, abstractmethod
from ..window_pipeline import data_processing
from typing import Dict


class ModelBase(ABC):
    def __init__(self, asset):
        self.window = data_processing(asset)
        self.model = self.build_model()

    @abstractmethod
    def build_model(self):
        pass

    @abstractmethod
    def to_dict(self) -> Dict:
        pass
