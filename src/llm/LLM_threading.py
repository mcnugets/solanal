from collections import deque
from threading import Thread, Event
from queue import Queue
from threading import Lock, Condition
from LLM_processor import llm_analyser
from src import Parcel
from src import ScraperLogger as logger


class llm_threader:

    def __init__(self, input_queue: Queue, logger: logger, llm_anal: llm_analyser):

        self.input_queue = input_queue
        self.llm_anal = llm_anal
        self.data_buffer = deque(maxlen=100)

        self.data_lock = Lock()  # For data_buffer access
        self.buffer_lock = Lock()  # For driver operations
        self.analyse_lock = Lock()  # For processing synchronization
        self.condition = Condition()  # For efficient waiting

        self.stop_event = Event()

        self.logger = logger

    def start_workers(self):

        threads = [Thread(target=self.fetch_data), Thread(target=self.process_llm)]
        for thread in threads:
            thread.start()

    def fetch_data(self):
        while not self.stop_event.is_set():
            try:
                with self.buffer_lock:
                    if len(self.data_buffer) == 100:
                        with self.condition:
                            self.condition.wait()

                    data: Parcel = self.input_queue.get()
                    data_dict = data.model_dump()

                    self.data_buffer.append(data_dict)
                    self.input_queue.task_done()
                    with self.condition:
                        self.condition.notify()

            except Exception as e:
                self.logger.log_error(
                    error_msg="Analysis failed to be performed: llm_threading",
                    exc_info=e,
                )

    def process_llm(self):
        while not self.stop_event.is_set():
            data = None
            try:
                with self.buffer_lock:
                    while not self.data_buffer and not self.stop_event.is_set():
                        with self.condition:
                            self.condition.wait()

                    if self.data_buffer:
                        data = self.data_buffer.pop()

                if data is not None:
                    with self.analyse_lock:
                        self.llm_anal.analyse(data)
            except Exception as e:
                self.logger.log_error(error_msg="process_llm() failed", exc_info=e)
                raise RuntimeError("process_llm() failed")

    def stop(self):
        self.stop_event.set()

        if self.threads:
            for thread in self.threads:
                thread.join()
