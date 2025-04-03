from queue import Queue
from threading import Thread, Event, Lock
from typing import Dict, List
import logging
import time
from ..data.models import Pair_data, Parcel
from ..core.logger import ScraperLogger as log


class DataCompiler:

    def __init__(
        self,
        input_queues: Dict[str, Queue],
        output_queue: Queue,
        logger: log,
        required_sources: List[str] = ["gmgn2", "solscan"],
    ):
        self.input_queues = input_queues
        self.output_queue = output_queue
        self.required_sources = required_sources
        self.stop_event = Event()
        self.data_lock = Lock()
        self.compiled_data = {}
        self.pending_addresses = set()  # Track addresses being processed
        self.thread = None
        self.logger = logger

    def start(self):
        self.thread = Thread(target=self._compile_data)
        self.thread.start()

    def _compile_data(self):
        while not self.stop_event.is_set():
            try:
                self._process_input_queues()
                self._process_complete_entries()

            except Exception as e:
                logging.error(f"Critical error in compilation loop: {e}")
                time.sleep(0.1)  # Prevent tight loop on errors

    def _process_input_queues(self):
        """Handle input queue processing with dedicated error handling"""
        for source in self.required_sources:
            try:

                if not self.input_queues[source].empty():
                    data = self.input_queues[source].get()
                    self._process_single_data(source, data)
            except Exception as e:
                logging.error(f"Error processing queue {source}: {e}")
                continue

    def _process_single_data(self, source: str, data: Pair_data):
        """Process single data item with synchronization"""
        try:
            with self.data_lock:
                if isinstance(data, Pair_data):
                    address = self._extract_address(data.raw_data)
                    if address:
                        # Add to pending if new
                        self.pending_addresses.add(address)

                        # Store the data
                        if address not in self.compiled_data:
                            self.compiled_data[address] = {}
                        self.compiled_data[address][source] = data
                        logging.info(f"Stored {source} data for address {address}")

                        # Check if we have all sources
                        if self._check_complete(address):
                            self._output_data(address)

        except Exception as e:
            logging.error(f"Error processing data from {source}: {e}")

    def _check_complete(self, address: str) -> bool:
        """Check if we have all required sources for an address"""
        return set(self.compiled_data[address].keys()) == set(self.required_sources)

    def _output_data(self, address: str):
        """Output complete data and cleanup"""
        try:
            combined_data = self._combine_data(self.compiled_data[address])
            self.output_queue.put(combined_data)
            logging.info(f"Output complete data for {address}")

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
                    # Simple check for all required sources
                    if set(sources.keys()) == set(self.required_sources):
                        try:
                            combined_data = self._combine_data(sources)
                            self.output_queue.put(combined_data)
                            logging.info(
                                f"Compiled data from all sources for {address}"
                            )
                            self.logger.log_queue_status(
                                "FINAL QUEUE", self.output_queue
                            )
                            del self.compiled_data[address]
                        except Exception as e:
                            logging.error(f"Error combining data for {address}: {e}")
                    else:
                        missing = set(self.required_sources) - set(sources.keys())
                        # logging.info(f"Address {address} missing sources: {missing}")
            except Exception as e:
                logging.error(f"Error processing entries: {e}")

    def _combine_data(self, sources: Dict[str, Pair_data]) -> Parcel:
        """Combine data from different sources into a single Pair_data object"""
        combined = {
            "gmgn2_data": sources["gmgn2"].raw_data,
            # "gmgn_data": sources["gmgn"].raw_data,
            "solscan_data": sources["solscan"].raw_data,
        }
        return Parcel(data_combined=combined)

    def _extract_address(self, data: str | List[str]) -> str:
        """Extract address from data string"""
        try:
            if isinstance(data, str) and "#" in data:
                return data.split("#")[-1]
            if isinstance(data, list):
                return data[-1]
            return None
        except Exception as e:
            logging.error(f"Error extracting address: {e}")
            return None

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
