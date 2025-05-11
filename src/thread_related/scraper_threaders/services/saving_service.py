from src.data.models import Address_Data as ad
from src.core.logger import ScraperLogger as log
from src.thread_related.scraper_threaders.services.base_service import base_service
from src.DataFrameManager import DataFrameManager as dfm
from src.thread_related.scraper_threaders.services.resources import (
    thread_resources,
    queue_resources,
)
from src.thread_related.scraper_threaders.Ithreader import Idata_validator
from queue import Queue
from typing import List


class saving_service(base_service):

    def __init__(
        self,
        df_manager: dfm,
        logger: log,
        thread_r: thread_resources,
        queue_r: queue_resources,
        data_validatoer: Idata_validator,
        columns: List[str] | None = None,
    ):
        super().__init__(logger, thread_r, queue_r)
        self.df_manager = df_manager
        self.data_validatoer = data_validatoer
        self.columns = columns

    def run(self, input_queue: Queue):
        while not self.thread_r.stop_event.is_set():
            try:
                with self.thread_r.condition:
                    if not self.queue_r.processed_queue.empty():

                        address_data: ad = self.queue_r.processed_queue.get(timeout=1)

                        self.logger.log_info(f"PROCESSED DATA: {address_data}")
                        self.logger.log_type_data(
                            "the processed data", None, address_data
                        )

                        processed = self.df_manager.process_data(data=address_data.data)
                        if not isinstance(processed, dict):
                            self.logger.log_error(
                                error_msg="invalid data row skipping",
                                exc_info=address_data.data,
                            )
                            continue

                        try:
                            data_row = self.data_validatoer.validate(processed)
                        except Exception as ve:
                            self.logger.log_error(
                                f"Validation failed, dropping row {processed}",
                                exc_info=ve,
                            )
                            continue
                        input_queue.put(data_row.model_dump())
                        input_queue.task_done()
                        # self.shared_condition.notify_all()
                        self.logger.log_info(
                            f"when inner queue is NOT empty: {data_row}"
                        )
                        self.logger.log_info(
                            f"the output queue size: {input_queue.qsize()}"
                        )

            except Exception as e:
                self.logger.log_error(error_msg=f"Error saving data: {e}")
                with self.thread_r.condition:
                    self.queue_r.processed_queue.put(address_data, timeout=1)
                    self.thread_r.condition.notify()

    def cleanup(self):
        pass
