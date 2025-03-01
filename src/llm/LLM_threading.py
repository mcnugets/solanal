from collections import deque
from threading import Thread, Event
from queue import Queue
from threading import Lock, Condition
from LLM_processor import llm_analyser


class llm_threader:
    def __init__(self, llm_anal: llm_analyser):

        self.queue = Queue()
        self.llm_anal = llm_anal

        self.data_lock = Lock()  # For data_buffer access
        self.driver_lock = Lock()  # For driver operations
        self.process_lock = Lock()  # For processing synchronization
        self.condition = Condition()  # For efficient waiting

    def start_workers(self):

        threads = [Thread(target=self.process_llm), Thread(target=self.run_llm)]
        for thread in threads:
            thread.start()

    def process_llm(self):
        while not self.stop_event.is_set():
            pass
        pass

    def run_llm(self):
        while not self.stop_event.is_set():
            pass
        pass
