from abc import ABC, abstractmethod
from queue import Queue


class Iservice(ABC):

    @abstractmethod
    def run(self, input_queue: Queue | None = None):
        """Run method that can work with or without queue"""
        pass
    def cleanup(self):
        """I guess thats a design flaw but i had to create cleanup meythod for centralisation purposes """
        pass