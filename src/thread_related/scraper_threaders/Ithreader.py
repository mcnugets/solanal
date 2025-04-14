from abc import ABC, abstractmethod
from typing import Any, Dict


class Idata_validator(ABC):
    @abstractmethod
    def validate(self, data: Dict):
        pass


class Ithreader(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start(self):
        pass


class Iwait_threader(ABC):

    @abstractmethod
    def wait(self):
        pass


class Iprocess_threader(ABC):
    @abstractmethod
    def process(self):
        pass


class Isave_threader(ABC):
    @abstractmethod
    def save(self):
        pass
