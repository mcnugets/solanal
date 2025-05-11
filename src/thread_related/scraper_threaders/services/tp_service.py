from src.data.models import Address_Data as ad
from src.core.logger import ScraperLogger as log
from src.thread_related.scraper_threaders.Ithreader import Iprocess_threader
from src.utils.TextProcessor import TextProcessor as tp
from src.thread_related.scraper_threaders.services.resources import (
    thread_resources,
    queue_resources,
)
from .base_service import base_service


class text_processor_service(base_service):

    def __init__(
        self,
        text_processor: tp,
        logger: log,
        thread_r: thread_resources,
        queue_r: queue_resources,
    ):
        super().__init__(logger, thread_r, queue_r)
        self.text_processor = text_processor

    def run(self):
        while not self.thread_r.stop_event.is_set():
            try:
                with self.thread_r.condition:
                    while self.queue_r.data_buffer.empty():
                        self.thread_r.condition.wait(timeout=1)
                        if self.thread_r.stop_event.is_set():
                            continue

                    address_data: ad = self.queue_r.data_buffer.get()

                    processed = self.text_processor.process(address_data.data)
                    address_data.data = processed

                    self.queue_r.processed_queue.put(address_data)

            except Exception as e:
                self.logger.log_error(error_msg=f"Error processing data: {e}")
                with self.thread_r.condition:
                    self.queue_r.data_buffer.put(address_data, timeout=1)
                    self.thread_r.condition.notify()

    def cleanup(self):
        pass
