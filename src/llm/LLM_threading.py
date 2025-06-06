from collections import deque
from threading import Thread, Event
from queue import Queue
from threading import Lock, Condition
from src.data.llm_model import valid_data
from src import ScraperLogger as logger
from src.llm.LLM_processor import llm_analyser
import threading


class llm_threader:
    """Thread manager for LLM analysis operations."""

    def __init__(
        self,
        input_queue: Queue,
        output_queue: Queue,
        logger: logger,
        llm_anal: llm_analyser
    ):
        """Initialize LLM threader with queues and analyzer."""
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.llm_anal = llm_anal
        self.data_buffer = deque(maxlen=100)

        # Thread synchronization primitives
        self.data_lock = Lock()  # For data_buffer access
        self.buffer_lock = Lock()  # For driver operations
        self.analyse_lock = Lock()  # For processing sync
        self.condition = Condition()  # For efficient waiting

        self.stop_event = Event()
        self.logger = logger
        self.threads = []

    def start_all(self):
        """Start all worker threads."""
        threads = [
            Thread(target=self.fetch_data),
            Thread(target=self.process_llm)
        ]
        for thread in threads:
            thread.start()
        self.threads = threads

    def fetch_data(self):
        """Fetch data from input queue and buffer it."""
        while not self.stop_event.is_set():
            try:
                self.logger.log_info(f"Thread {threading.current_thread().name} attempting to acquire buffer_lock for fetch.")
                with self.buffer_lock:
                    self.logger.log_info(f"Thread {threading.current_thread().name} acquired buffer_lock for fetch.")
                    if len(self.data_buffer) == 100:
                        with self.condition:
                            self.condition.wait()

                    data: valid_data = self.input_queue.get()
                    self.logger.log_info(f"Received data: {data}")
                    data_dict = data
                    self.data_buffer.append(data_dict)
                    self.input_queue.task_done()
                    with self.condition:
                        self.condition.notify()
                self.logger.log_info(f"Thread {threading.current_thread().name} released buffer_lock for fetch.")

            except Exception as e:
                self.logger.log_error(
                    error_msg="Analysis failed to be performed: llm_threading",
                    exc_info=e,
                )

    def process_llm(self):
        """Process buffered data through LLM analyzer."""
        while not self.stop_event.is_set():
            data = None
            try:
                self.logger.log_info(f"Thread {threading.current_thread().name} attempting to acquire buffer_lock for process.")
                with self.buffer_lock:
                    self.logger.log_info(f"Thread {threading.current_thread().name} acquired buffer_lock for process.")
                    self.logger.log_info('The buffer has been activated')
                    while not self.data_buffer and not self.stop_event.is_set():
                        with self.condition:
                            self.condition.wait()

                    if self.data_buffer:
                        data = self.data_buffer.pop()
                self.logger.log_info(f"Thread {threading.current_thread().name} released buffer_lock for process.")

                if data is not None:
                    with self.analyse_lock:
                        self.logger.log_info('Starting the LLM anal...')
                        msg = self.llm_anal.analyse(data)
                        self.logger.log_info(
                            'Data was delivered to the final QUEUE'
                        )
                        print(msg)
                        self.output_queue.put(msg)
                        self.output_queue.task_done()
            except Exception as e:
                self.logger.log_error(
                    error_msg="process_llm() failed",
                    exc_info=e
                )
                raise RuntimeError("process_llm() failed")

    def stop(self):
        """Stop all threads and clean up."""
        self.stop_event.set()
        if self.threads:
            for thread in self.threads:
                thread.join()
