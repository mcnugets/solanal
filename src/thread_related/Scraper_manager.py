from .Scraper_Threading import Scraper_Threading
from typing import List, Optional, Dict
from queue import Queue
from src.DataFrameManager import DataFrameManager as dfm
from src.utils.TextProcessor import TextProcessor as tp
import time
from threading import Event, Lock, Condition
from src.core.logger import ScraperLogger

from src.scrapers.GMGN_processor import gmgn_processor
from src.scrapers.PumpFun_processor import pumpfun_processor
from src.scrapers.solscan_scraper import solscan_processor


from src.thread_related.scraper_threaders.Ithreader import Ithreader


class Scraper_Manager:

    def __init__(self, logger: ScraperLogger, shared_state: Dict):

        self.shared_condition = Condition()
        self.scrapers: List[Scraper_Threading] = []
        self.logger = logger
        self.shared_event = Event()
        self.shared_lock = Lock()
        self.shared_state = shared_state

    def add_scraper(
        self,
        config,
        columns,
        patterns,
        cleaning_patterns,
        base_file,
        input_queue,
        output_queue,
    ):
        # if self.is_initialized:
        #     return self.scraper_thread

        scraper_type = config.get("type")
        config.pop("type")
        print(globals().keys())
        scraper_class = globals()[f"{scraper_type}_processor"]  # Get class by name

        scraper = scraper_class(**config)

        df_manager = None
        text_processor = None

        if columns and base_file:
            try:
                df_manager = dfm(columns=columns, base_file=base_file)
            except Exception as e:
                print(f"Error initializing DataFrameManager: {e}")
                self.logger.log_error(
                    error_msg=f"Error initializing DataFrameManager", exc_info=e
                )

        if cleaning_patterns and patterns:
            try:
                text_processor = tp(
                    patterns=patterns, CLEANING_PATTERNS=cleaning_patterns
                )
            except Exception as e:
                print(f"Error initializing TextProcessor: {e}")
                self.logger.log_error(
                    error_msg=f"Error initializing TextProcessor", exc_info=e
                )

        scraper_thread = Scraper_Threading(
            type=scraper_type,
            df_manager=df_manager,
            text_processor=text_processor,
            scraper=scraper,
            columns=columns,
            input_queue=input_queue,
            output_queue=output_queue,
            shared_condition=self.shared_condition,
            shared_state=self.shared_state,
        )
        self.scrapers.append(scraper_thread)

    def add_scraper_v2(self, threader: Ithreader) -> None:

        try:
            self.scrapers.append(threader)
            self.logger.log_info(f"Added new scraper threader: {threader.name}")
        except Exception as e:
            self.logger.log_error(
                error_msg=f"Error adding new scraper threader: {threader.name}",
                exc_info=e,
            )

    def start_all(self):

        for scraper in self.scrapers:
            scraper.scrape_dat_bitch()

        # self.scraper_thread = self._init_scraper()
        # self.scraper_thread.scrape_dat_bitch()

    def stop_all(self):
        for scraper in self.scrapers:
            scraper.stop()

        # if self.scraper_thread:
        #     self.scraper_thread.stop()
        #     self.scraper_thread = None

    def monitor(self):
        try:
            while not self.stop_event.is_set():
                if not self.scraper_thread.processed_queue.empty():
                    print(self.scraper_thread.processed_queue.get())
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop_event.set()
