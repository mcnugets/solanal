from queue import Queue
from typing import Dict, Optional, Union, List


class queue_manager:
    def __init__(self):
        # A dictionary to hold multiple queues, keyed by a descriptive name
        self.queues: Dict[str, Dict[str, Queue]] = {}

    def add_queue(self, name: Union[str, List[str]]) -> None:
        """
        Create and add a new queue pair (input and output) under the given name.
        """
        if isinstance(name, str):
            self.queues[name] = {"inner_queue": Queue(), "output_queue": Queue()}
        if isinstance(name, List):
            for n in name:
                self.queues[n] = {"inner_queue": Queue(), "output_queue": Queue()}

    def get_queue(self, name: str) -> Dict[str, Queue]:
        """
        Retrieve the queue pair (input and output) for the given name.
        """
        return self.queues.get(name, {})

    def get_all_queues(self) -> Dict[str, Dict[str, Queue]]:
        """
        Return the entire dictionary of queues.
        """
        return self.queues
