from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Optional, Dict, List
import re
import numpy as np
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchWindowException,
)
from collections import deque
from threading import Thread, Event
from queue import Queue
from src.DataFrameManager import DataFrameManager as dfm
import undetected_chromedriver as uc
from threading import Lock, Condition
import logging

# Custom
from src.TextProcessor import TextProcessor as tp
from colorama import init, Fore, Back, Style
from src.Base_scraper import Base_scraper

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
        columns: List[str],
        output_queue: Queue,
        inner_queue: Optional[Queue] = None,
        df_manager: Optional[dfm] = None,
        text_processor: Optional[tp] = None,
        scraper: Optional[Base_scraper] = None,
    ):

        self.columns = columns
        self.scraper = scraper

        self.data_buffer = []
        self.processed_queue = Queue()
        self.stop_event = Event()
        self.driver = None

        self.df_manager = df_manager
        self.text_processor = text_processor

        self.stop_event.set()  # Set to true, so by default it is not paused

        self.data_lock = Lock()  # For data_buffer access
        self.driver_lock = Lock()  # For driver operations
        self.process_lock = Lock()  # For processing synchronization
        self.condition = Condition()  # For efficient waiting
        self.threads = []

        self.output_queue = output_queue
        self.inner_queue = inner_queue

    def scrape_dat_bitch(self):
        # Define a mapping of method names to thread targets
        method_mapping = {
            "start_scraping": self.start_scraping,
        }

        # Add _process_data to method_mapping if text_processor is present
        if self.text_processor:
            method_mapping["_process_data"] = self._process_data

        # Add _save_data to method_mapping if df_manager is present
        if self.df_manager:
            method_mapping["_save_data"] = self._save_data

        # Dynamically create threads for methods that exist
        for method_name, method in method_mapping.items():
            if hasattr(self, method_name):
                self.threads.append(Thread(target=method))

        # Start all threads
        for thread in self.threads:
            thread.start()

    def start_scraping(self):

        try:

            with self.driver_lock:  # Protect driver initialization
                self.scraper.setup_website()

                while not self.stop_event.is_set():
                    try:

                        scrape_gen = self.scraper._scrape_data()
                        temp_data = next(scrape_gen)  # Get the next piece of data
                        print(f"Processing data: {temp_data}")
                        with self.condition:
                            while len(self.data_buffer) >= 1000:
                                self.condition.wait()
                            self.data_buffer.append(temp_data)
                            self.condition.notify_all()
                            # Add data and notify

                    except StopIteration:
                        # Generator exhausted
                        break

                    except Exception as e:
                        print(f"Scraping error: {e}")
                        time.sleep(1)  # Prevent tight error loop

        finally:
            if self.scraper.driver:
                self.scraper.driver.quit()

    # def fetch_token_data(self):
    #     while not self.stop_event.is_set():
    #         try:
    #             gmgn_scrape = self.scraper.fetch_token_data()
    #             raw_data = next(gmgn_scrape)
    #             self.data_buffer_2.append(raw_data)
    #         except Exception as e:
    #             print(f"An error occurred: {e}")

    def _process_data(self):
        while not self.stop_event.is_set():
            with self.condition:
                while not self.data_buffer:
                    self.condition.wait(timeout=1)
                    if self.stop_event.is_set():
                        return
                raw_data = self.data_buffer.pop(0)

            try:
                processed = self.text_processor.process(raw_data)
                self.processed_queue.put(processed)
            except:
                with self.condition:
                    self.data_buffer.append(raw_data)
                    self.condition.notify()

    # post-processings
    def _save_data(self):

        while not self.stop_event.is_set():
            try:
                if not self.processed_queue.empty():
                    new_data = self.processed_queue.get(timeout=1)

                    with self.process_lock:  # Protect dataframe access#
                        # extra_data ={ data} data = [data1, data2]
                        # extra_data = {data}, data= [data1, data2, data3]
                        if self.inner_queue is None:
                            self.output_queue.put((new_data))
                            logging.info(f"IN SCRAPER THREADING: {new_data}")
                        else:
                            old_data = self.inner_queue.get()
                            self.output_queue.put((new_data, old_data))
                            logging.info(f"IN SCRAPER THREDING 2: {new_data}")
                            logging.info(f"IN SCRAPER THREDING 2: {old_data}")

                        self.df_manager.process_data(
                            new_data, columnname=self.columns[0]
                        )
            except Exception as e:
                msg = f"The error: {e}"
                print(msg)
                # logging.error(msg)

    def stop(self):

        self.stop_event.set()

        if self.threads:
            for thread in self.threads:
                thread.join()
        self.scraper.cleanup()
