from queue import Queue
from threading import Event, Thread, Lock, Condition
from src.data.models import Address_Data as ad
from src.scrapers.Base_scraper import Base_scraper
from src.core.logger import ScraperLogger as log
from abc import abstractmethod, ABC
from .Ithreader import Ithreader
from src.thread_related.scraper_threaders.services.resources import (
    thread_resources,
    queue_resources,
)


class base_threader(Ithreader, ABC):

    def __init__(
        self,
        name: str,
        logger: log,
        thread_r: thread_resources,
        queue_r: queue_resources,
        input_queue: Queue | None = None,
        output_queue: Queue | None = None,
    ):
        self.logger = logger
        self._name = name

        self.threads = []
        self.method_mapping = {}

        self.thread_r = thread_r
        self.queue_r = queue_r

        self.input_queue = input_queue
        self.output_queue = output_queue

    @property
    def name(self) -> str:
        return self.name

    def register_method(self, mehod_name, method):
        self.method_mapping[mehod_name] = method

    def start(self):
        try:

            for method_name, method in self.method_mapping.items():
                if hasattr(self, method_name):
                    self.threads.append(Thread(target=method))

            # Start all threads
            for thread in self.threads:
                thread.start()
        except Exception as e:
            self.logger.log_error(error_msg="failed to initialise threads", exc_info=e)

    def stop(self):
        try:
            self.logger.log_info(f"Stopping {self.name} threads...")
            self.thread_r.stop_event.set()

            if self.threads:
                for thread in self.threads:
                    if thread.is_alive():
                        thread.join(timeout=5.0)  # Add timeout to prevent hanging
                        if thread.is_alive():
                            self.logger.log_warning(
                                f"Thread {thread.name} did not terminate properly"
                            )

            self.threads.clear()  # Clean up the threads list
            self.logger.log_info(f"All {self.name} threads stopped")
            self.cleanup()
        except Exception as e:
            self.logger.log_error(
                error_msg=f"Error stopping {self.name} threads", exc_info=e
            )
            raise
  
    def cleanup(self):
        pass