from queue import Queue
from threading import Thread, Event, Lock
from typing import Dict, List, Set, ClassVar
import logging
import time
from src.core.logger import ScraperLogger as log
from src.data.llm_model import valid_data
from src.data.models import Address_Data, Parcel
from pydantic import BaseModel, field_validator
from src.thread_related.distributor import dsitributor


class validate_sources(BaseModel):
    pumpfun: str | None = None
    gmgn_2: str | None = None
    gmgn: str | None = None
    holders: str | None = None

    _allowed_sources: ClassVar[Set[str]] = {
        "pumpfun", "gmgn_2", "gmgn", "holders"
    }

    @field_validator("pumpfun", "gmgn_2", "gmgn", "holders", mode="after")
    @classmethod
    def check_sources(cls, v) -> str:
        if not isinstance(v, str):
            raise TypeError("Sources must be a string")
        if v not in cls._allowed_sources:
            raise ValueError(f"Invalid source: {v}")
        return v

    class Config:
        arbitrary_types_allowed = True


class DataCompiler:
    def __init__(
        self,
        input_queues: Dict[str, Queue],
        output_queue: Queue,
        logger: log,
        data_sources: validate_sources,
        dsitributor: dsitributor,
        topic: str,
    ):
        self.input_queues = input_queues
        self.output_queue = output_queue
        self.required_sources = list(
            data_sources.model_dump(exclude_none=True).values()
        )
        self.stop_event = Event()
        self.data_lock = Lock()
        self.compiled_data = {}
        self.pending_addresses = set()
        self.thread = None
        self.logger = logger
        self.distributor = dsitributor
        
        self.logger.log_warning(
            "Input queues configuration: "
            f"{ {k: str(v) for k, v in self.input_queues.items()} }"
        )
        self.logger.log_warning(
            "CHECKING IF THE INPUT QUEUE NULL OR NOT: "
            f"{type(self.input_queues.get(topic))}"
        )
        self.logger.log_info(
            f"Queue for topic '{topic}': "
            f"{str(self.input_queues.get(topic))}"
        )
        self.distributor.subscribe(
            topic=topic,
            queue=self.input_queues[topic],
            queue_name='data_compiler'
        )

    def start(self):
        self.logger.log_info('Starting data compiler...')
        self.thread = Thread(target=self._compile_data)
        self.thread.start()

    def _compile_data(self):
        while not self.stop_event.is_set():
            try:
                self._process_input_queues()
                self._process_complete_entries()
            except Exception as e:
                logging.error(f"Critical error in compilation loop: {e}")
                time.sleep(0.1)

    def _process_input_queues(self):
        """Handle input queue processing with dedicated error handling"""
        for source in self.required_sources:
            try:
                if not self.input_queues[source].empty():
                    data = self.input_queues[source].get()
                    self.logger.log_info(
                        f"Processing data from {source} "
                        f"(queue size now: {self.input_queues[source].qsize()})"
                    )
                    self._process_single_data(source, data)
            except KeyError as e:
                self.logger.log_error(
                    f"Missing queue configuration for required source {source}: {e}"
                )
                continue
            except Exception as e:
                self.logger.log_error(
                    f"Error processing queue {source}: {str(e)}",
                    exc_info=True
                )
                continue

    def _process_single_data(self, source: str, data: Address_Data):
        """Process single data item with synchronization"""
        try:
            with self.data_lock:
                self.logger.log_info('checkung data lock threader data cmpiler')

                self.logger.log_info('checking if isinstance is being True')
                address = self._extract_address(data)
                if address:
                    self.pending_addresses.add(address)
                    if address not in self.compiled_data:
                        self.compiled_data[address] = {}
                    self.compiled_data[address][source] = data.data
                    self.logger.log_info(f"Stored {source} data for address {address}")

                    logging.info(f"Stored {source} data for address {address}")
                    if self._check_complete(address):
                        self._output_data(address)
        except Exception as e:
            logging.error(f"Error processing data from {source}: {e}")

    def _check_complete(self, address: str) -> bool:
        """Check if we have all required sources for an address"""
        return (set(self.compiled_data[address].keys()) == 
                set(self.required_sources))

    def _output_data(self, address: str):
        """Output complete data and cleanup"""
        try:
            combined_data = self._combine_data(self.compiled_data[address])
            self.output_queue.put(combined_data)
            self.logger.log_info(f"Output complete data for {address}")
            self.logger.log_queue_status("FINAL QUEUE", self.output_queue)
            del self.compiled_data[address]
            self.pending_addresses.remove(address)
        except Exception as e:
            logging.error(f"Error outputting data for {address}: {e}")

    def _process_complete_entries(self):
        """Process entries that have all three required sources"""
        with self.data_lock:
            try:
                for address, sources in list(self.compiled_data.items()):
                    if set(sources.keys()) == set(self.required_sources):
                        self.logger.log_info('FINAL SETP OF COMPILING DATAS')
                        try:
                            combined_data = self._combine_data(sources)
                            self.output_queue.put(combined_data)
                            self.logger.log_info(
                                f"Compiled data from all sources for {address}"
                            )
                            self.logger.log_queue_status(
                                "FINAL QUEUE", self.output_queue
                            )
                            del self.compiled_data[address]
                        except Exception as e:
                            self.logger.log_error(f"Error combining data for {address}: {e}")
                 
            except Exception as e:
                logging.error(f"Error processing entries: {e}")

    def _combine_data(self, sources: Dict[str, BaseModel]) -> Parcel:
        """Combine data from different sources into a single Pair_data object"""
        try:
            combined = {
                keys: sources[keys] for keys in self.required_sources
            }
            return valid_data(**combined)
        except KeyError as e:
            self.logger.log_error(f"Missing required source in data: {e}")
            raise ValueError(f"Missing required source data: {e}")
        except Exception as e:
            self.logger.log_error(f"Error combining data sources: {e}")
            raise RuntimeError(f"Failed to combine data: {e}")

    def _extract_address(self, data: Address_Data) -> str:
        """Extract address from data string"""
        try:
            address = data.address
            self.logger.log_info(f"Successfully extracted address: {address}")
            return address
        except Exception as e:
            logging.error(f"Error extracting address: {e}")
            return None

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
