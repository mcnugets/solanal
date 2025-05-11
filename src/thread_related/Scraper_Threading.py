from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Optional, Dict, List, Tuple, Union
import re
import numpy as np
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchWindowException,
)
from collections import deque
from threading import Thread, Event
from queue import Queue, Empty
from src.DataFrameManager import DataFrameManager as dfm
import undetected_chromedriver as uc
from threading import Lock, Condition
import logging
from pathlib import Path

# Custom
from src.utils.TextProcessor import TextProcessor as tp
from colorama import init, Fore, Back, Style

from src.scrapers.Base_scraper import Base_scraper
from src.data.models import Pair_data
from src.core.logger import ScraperLogger as log

logger = log()

init()

# CLEANING_PATTERNS = {
#     r"\s+": "",  # Remove whitespace
#     r"\n+": "#",  # Replace newlines with hash
#     r"#+": "#",  # Normalize multiple hashes
#     r"^\#|\#$": "",  # Remove leading/trailing hashes
#     r"(.)\1+": r"\1",
# }
CLEANING_PATTERNS = {
    r"\n+": "#",  # Replace newlines with hash
    r"#+": "#",  # Normalize multiple hashes
    r"^\#|\#$": "",  # Remove leading/trailing hashes
    r"(.)\1+": r"\1",
}


# the way this works:
# pass one main queue for adding the elements
# and each inherited class would have extra param in constructor for output queue
class Scraper_Threading:

    def __init__(
        self,
        type: str,  # we use this for tracking the type of scraper
        columns: List[str],
        output_queue: Queue[Pair_data | None],
        input_queue: Optional[Queue] = None,
        df_manager: Optional[dfm] = None,
        text_processor: Optional[tp] = None,
        scraper: Optional[Base_scraper] = None,
        shared_state: Optional[Dict] = None,  # Add shared state
        shared_condition: Optional[Condition] = None,
        turn_finished: Optional[Event] = None,
        shared_lock: Optional[Lock] = None,
    ):
        self.columns = columns
        self.scraper = scraper

        self.data_buffer = Queue(maxsize=100)
        self.processed_queue: Queue = Queue()
        self.stop_event = Event()
        self.driver = None

        self.save_trigger = Event()

        self.df_manager = df_manager
        self.text_processor = text_processor

        self.data_lock = Lock()  # For data_buffer access
        self.driver_lock = Lock()  # For driver operations
        self.process_lock = Lock()  # For processing synchronization
        self.condition = Condition()  # For efficient waiting
        self.threads = []

        self.output_queue = output_queue

        self.input_queue = input_queue
        self.deque = deque(maxlen=100)

        self.is_input_queue = False

        self.type = type
        self.shared_state = shared_state or {}
        self.shared_lock = shared_lock or Lock()

        self.turn_finished = turn_finished
        self.shared_condition = shared_condition or Condition()

        self.process_turn = ["pumpfun", "gmgn", "solscan"]

    def scrape_dat_bitch(self):
        method_mapping = {}  # Start with an empty dictionary

        # Add "wait_event" first if self.input_queue is True
        if self.input_queue:
            method_mapping["wait_event"] = self.wait_event

        # Add other methods
        method_mapping["start_scraping"] = self.start_scraping
        method_mapping["_process_data"] = self._process_data
        method_mapping["_save_data"] = self._save_data

        # Dynamically create threads for methods that exist
        for method_name, method in method_mapping.items():
            if hasattr(self, method_name):
                self.threads.append(Thread(target=method))

        # Start all threads
        for thread in self.threads:
            thread.start()

    def wait_event(self):
        while not self.stop_event.is_set():
            try:

                # thing thing needs to be fixed for base cases
                # pair_data: Pair_data = self.input_queue.get(
                #     timeout=2
                # )  # Wait for data with timeout
                data = self.input_queue.get(timeout=2)
                self.is_input_queue = True
                address = data["full_address"]
                logging.info(f"DATA ADDED FROM THE PASSED QUEUE: {data}")
                logger.log_type_data("the gotten data", self.type, data)
                with self.shared_lock:
                    # Track which scraper processed this address
                    if address not in self.shared_state:
                        self.shared_state[address] = set()
                    self.shared_state[address].add(self.type)

                    logger.log_sync_event(
                        f"Type {self.type} processing {address}. "
                        f"Processed by: {self.shared_state[address]}"
                    )

                    with self.data_lock:
                        # self.deque.append(address)
                        # self.deque.append((pair_data, address))

                        print("testing if this works")
                        if self.scraper is None:
                            logging.error("Scraper is not initialized")
                            return
                        self.scraper._deque.append((data, address))
                        with self.condition:
                            self.condition.notify_all()  # Notify that deque has data

            except Empty:
                logging.info("Input queue is empty, waiting for data...")
                continue  # Continue waiting for data

            except Exception as e:
                logging.error(f"Error handling wait event: {e}")
                return

    def start_scraping(self):
        try:
            if self.input_queue:
                with self.condition:
                    while (
                        self.scraper._deque.__len__() <= 0
                        and not self.stop_event.is_set()
                    ):
                        self.condition.wait()

            if self.stop_event.is_set():
                return
            with self.driver_lock:  # Protect driver initialization
                self.scraper.setup_website()

                while not self.stop_event.is_set():
                    try:
                        if self.input_queue and not self.is_input_queue:
                            #  we found the loop hole
                            logging.info("Starting scraping...")
                            self.condition.wait(
                                timeout=2
                            )  # Prevent tight loop if input queue is empty
                            # continue

                        scrape_gen = self.scraper._scrape_data()
                        temp_pair_data: Pair_data = next(
                            scrape_gen
                        )  # Get the next piece of data
                        logger.log_type_data(
                            "the scraped data", self.type, temp_pair_data
                        )
                        with self.condition:
                            while self.data_buffer.full():
                                self.condition.wait()
                            if self.type == "solscan":
                                logger.log_queue_status(
                                    "THIS IS IN START SRAPING", self.data_buffer
                                )
                            self.data_buffer.put(temp_pair_data)

                            self.condition.notify_all()
                            # Add data and notify

                    except StopIteration:
                        # Generator exhausted
                        time.sleep(1)
                        continue

                    except Exception as e:
                        print(f"Scraping error: {e}")
                        logging.error(f"Scraping error: {e}")
                        time.sleep(1)  # Prevent tight error loop

        finally:
            if self.scraper.driver:
                self.scraper.driver.quit()

    def _process_data(self):
        while not self.stop_event.is_set():
            try:
                if self.type == "solscan":
                    logger.log_queue_status(
                        "THIS IS IN PROCESS-DARTA", self.data_buffer
                    )
                with self.condition:
                    while self.data_buffer.empty():
                        self.condition.wait(timeout=1)
                        if self.stop_event.is_set():
                            continue
                    if self.type == "solscan":
                        logger.log_queue_status("SOLSCAN ACTIVATED 3", self.data_buffer)
                    # (raw_data, old_data) = self.data_buffer.get()
                    pair_data: Pair_data = self.data_buffer.get()
                    if self.text_processor:
                        processed = self.text_processor.process(pair_data.raw_data)
                        pair_data.raw_data = processed

                    if self.type == "solscan":
                        logger.log_queue_status("PROCESSED QUEUE", self.processed_queue)
                    self.processed_queue.put(pair_data)
                    # self.save_trigger.set()
            except Exception as e:
                logging.error(f"Error processing data: {e}")
                with self.condition:
                    self.data_buffer.put(pair_data, timeout=1)
                    self.condition.notify()

    def _save_data(self):
        while not self.stop_event.is_set():
            try:
                with self.shared_condition:
                    if not self.processed_queue.empty():

                        # if (
                        #     self.type != self.shared_state["current turn"]
                        #     and not self.stop_event.is_set()
                        # ):
                        #     self.shared_condition.wait()

                        pair_data: Pair_data = self.processed_queue.get(timeout=1)

                        logging.info(f"PROCESSED DATA: {pair_data}")
                        logger.log_type_data("the processed data", self.type, pair_data)

                        if self.type != "solscan":
                            data_row = self.df_manager.process_data(
                                data=pair_data.raw_data,
                                columnname=self.columns[0],
                            )
                        else:
                            data_row = pair_data.raw_data
                        self.output_queue.put(data_row)
                        self.output_queue.task_done()
                        self.shared_condition.notify_all()
                        logging.info(f"when inner queue is NOT empty: {data_row}")
                        logging.info(
                            f"the output queue size: {self.output_queue.qsize()}"
                        )
                        idx = self.process_turn.index(self.type) + 1
                        if idx >= len(self.process_turn):
                            idx = 0
                        self.shared_state["current turn"] = self.process_turn[
                            idx % len(self.process_turn)
                        ]

            except Exception as e:
                msg = f"The error: {e}"
                print(msg)

    def stop(self):
        self.stop_event.set()

        if self.threads:
            for thread in self.threads:
                thread.join()
        self.scraper.cleanup()
