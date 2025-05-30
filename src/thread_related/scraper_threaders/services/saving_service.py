from src.data.models import Address_Data as ad
from src.core.logger import ScraperLogger as log
from src.thread_related.scraper_threaders.services.base_service import (
    base_service
)
from src.DataFrameManager import DataFrameManager as dfm
from src.thread_related.scraper_threaders.services.resources import (
    thread_resources, queue_resources,
)
from src.thread_related.scraper_threaders.Ithreader import Idata_validator
from queue import Queue
from typing import List
from src.thread_related.distributor import dsitributor


class saving_service(base_service):

    def __init__(
        self,
        df_manager: dfm,
        logger: log,
        thread_r: thread_resources,
        queue_r: queue_resources,
        data_validatoer: Idata_validator,
        distributor: dsitributor,
        topic: str,
        columns: List[str] | None = None,
    ):
        super().__init__(logger, thread_r, queue_r)
        self.df_manager = df_manager
        self.data_validatoer = data_validatoer
        self.columns = columns
        self.distributor = distributor  
        self.topic = topic

    def run(self, input_queue: Queue | None = None, 
            local_queue: Queue | None = None,):
        while not self.thread_r.stop_event.is_set():
            try:
                with self.thread_r.condition:
                    if not local_queue.empty():
                        address_data: ad = local_queue.get(
                            timeout=1
                        )

                        self.logger.log_info(f"PROCESSED DATA: {address_data}")
                        self.logger.log_type_data(
                            "the processed data", None, address_data
                        )

                        processed = self.df_manager.process_data(
                            data=address_data.data
                        )
                        if (not isinstance(processed, dict)  
                            and not isinstance(processed, list)):
                            self.logger.log_error(
                                error_msg="invalid data row skipping",
                                exc_info=address_data.data,
                            )
                            continue

                        try:
                            # TODO: A TEMPORARY SOLUTION CHNAGE IT LATER ONCE THE CODE IS RAN
                            if isinstance(processed, list):
                                processed = processed[0]
                            data_row = self.data_validatoer.validate(processed)
                            address_data.data = data_row
                        except Exception as ve:
                            self.logger.log_error(
                                f"Validation failed, dropping row {processed}",
                                exc_info=ve,
                            )
                            continue

                        if not input_queue:
                            self.distributor.publish(
                                topic=self.topic, data=address_data
                            )
  
                        else:
                            input_queue.put(address_data)
                            input_queue.task_done()

                            self.logger.log_info(
                            f"the output queue size: {input_queue.qsize()}"
                            )

                            self.logger.log_info(
                                f"when inner queue is NOT empty: {data_row}"
                            )
                        

            except Exception as e:
                self.logger.log_error(error_msg=f"Error saving data: {e}")
                with self.thread_r.condition:
                    self.queue_r.processed_queue.put(address_data, timeout=1)
                    self.thread_r.condition.notify()

    def cleanup(self):
        pass
