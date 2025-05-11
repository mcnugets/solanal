from .base_service import base_service
from src.core.logger import ScraperLogger as log
from queue import Queue, Empty
from src.thread_related.scraper_threaders.services.resources import (
    thread_resources,
    queue_resources,
)
from src.data.models import Address_Data as ad
from src.scrapers.Base_scraper import Base_scraper


class wait_service(base_service):
    def __init__(
        self,
        logger: log,
        thread_r: thread_resources,
        queue_r: queue_resources,
        scraper: Base_scraper | None = None,
        is_input_queue: bool = False,
    ):
        super().__init__(logger, thread_r, queue_r, scraper, is_input_queue)

    def run(self, input_queue: Queue):
        while not self.thread_r.stop_event.is_set():
            try:

                data = input_queue.get(timeout=2)
                self.logger.log_info(data["full_address"])
                validated_data = ad(data=data, address=data["full_address"])
                self.is_input_queue = True
                self.logger.log_info(f"DATA ADDED FROM THE PASSED QUEUE: {data}")
                self.logger.log_info(f"the gottem data")

                with self.thread_r.data_lock:
                    # self.deque.append(address)
                    # self.deque.append((pair_data, address))

                    if self.scraper is None:
                        self.logger.log_error(error_msg="Scraper is not initialized")
                        return
                    # change this to proper encapsualtion solution rather direct access
                    self.scraper._deque.append(validated_data)
                    with self.thread_r.condition:
                        self.thread_r.condition.notify_all()  # Notify that deque has data}

            except Empty:
                self.logger.log_info("Input queue is empty, waiting for data...")
                continue  # Continue waiting for data

            except Exception as e:
                self.logger.log_error(
                    error_msg=f"Error handling wait event: ", exc_info=e
                )
                return

    def cleanup(self):
        pass
