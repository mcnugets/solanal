from src.Scraper_Threading import Scraper_Threading
from typing import List, Optional
from queue import Queue
from src.PumpFun_processor import pumpfun_processor
from src.GMGN_processor import gmgn_processor
from src.solscan_scraper import solscan_processor
from selenium.webdriver.common.by import By
from collections import deque
from threading import Event
from src.DataFrameManager import DataFrameManager as dfm
from src.TextProcessor import TextProcessor as tp
import signal
import time
from selenium.webdriver.support import expected_conditions as EC
from config import CLEANING_PATTERNS, configs, patterns, queue_m
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait

# TODO: things fo configer:
# TODO: use configs to set params
# TODO: better error handling
# TODO: add extra params: every what row to save,
# TODO: set the batches to process
# TODO: better logging output

# TODO: add web scraper to bubblemaps
# TODO: add web scraper to solsniffer
# TODO: add analyser code for twitter, and  tg


class Scraper_Manager:

    def __init__(
        self,
        config,
        columns,
        patterns,
        cleaning_patterns,
        base_file,
        output_queue,
        inner_queue: Optional[Queue] = None,
    ):

        self.config = config
        self.columns = columns
        self.patterns = patterns
        self.cleaning_patterns = cleaning_patterns
        self.base_file = base_file
        self.scraper_thread = None
        self.inner_queue = inner_queue
        self.output_queue = output_queue

    def _init_scraper(self):

        scraper_type = self.config.get("type")
        self.config.pop("type")
        print(globals().keys())
        scraper_class = globals()[f"{scraper_type}_processor"]  # Get class by name

        scraper = scraper_class(**self.config)

        df_manager = None
        text_processor = None

        if self.columns and self.base_file:
            try:
                df_manager = dfm(columns=self.columns, base_file=self.base_file)
            except Exception as e:
                print(f"Error initializing DataFrameManager: {e}")

        if self.cleaning_patterns and self.patterns:
            try:
                text_processor = tp(
                    patterns=self.patterns, CLEANING_PATTERNS=self.cleaning_patterns
                )
            except Exception as e:
                print(f"Error initializing TextProcessor: {e}")

        return Scraper_Threading(
            df_manager=df_manager,
            text_processor=text_processor,
            scraper=scraper,
            columns=self.columns,
            inner_queue=self.inner_queue,
            output_queue=self.output_queue,
        )

    def start(self):
        self.scraper_thread = self._init_scraper()
        self.scraper_thread.scrape_dat_bitch()

    def stop(self):
        if self.scraper_thread:
            self.scraper_thread.stop()
            self.scraper_thread = None

    def monitor(self):
        try:
            while not self.stop_event.is_set():
                if not self.scraper_thread.processed_queue.empty():
                    print(self.scraper_thread.processed_queue.get())
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop_event.set()


def signal_handler(sig, frame):
    global stop_event
    print("\nShutting down gracefully...")
    stop_event.set()


signal.signal(signal.SIGINT, signal_handler)
stop_event = Event()

gmgn_2_config = configs["gmgn_2"]
gmgn_config = configs["gmgn"]
solscan_config = configs["solscan"]


def extract_dynamic_table_data_2(columns: List[str] = None):
    global stop_event

    scrapers = [
        {
            "config": gmgn_2_config,
            "columns": columns[0],
            "patterns": patterns["patterns_gmgn_2"],
            "cleaning_patterns": CLEANING_PATTERNS,
            "base_file": "pumpfun_data.csv",
            "inner_queue": None,
            "output_queue": queue_m.get_queue("gmgn2")["output_queue"],
        },
        {
            "config": gmgn_config,
            "columns": columns[1],
            "patterns": patterns["patterns_gmgn"],
            "cleaning_patterns": CLEANING_PATTERNS,
            "base_file": "gmgn_data.csv",
            "inner_queue": queue_m.get_queue("gmgn")["inner_queue"],
            "output_queue": queue_m.get_queue("gmgn")["output_queue"],
        },
        {
            "config": solscan_config,
            "columns": "",
            "patterns": "",
            "cleaning_patterns": "",
            "base_file": "",
            "inner_queue": queue_m.get_queue("solscan")["inner_queue"],
            "output_queue": queue_m.get_queue("solscan")["output_queue"],
        },
    ]

    managers = [
        Scraper_Manager(
            config=scraper["config"],
            columns=scraper["columns"],
            patterns=scraper["patterns"],
            cleaning_patterns=scraper["cleaning_patterns"],
            base_file=scraper["base_file"],
            inner_queue=scraper["inner_queue"] if scraper["inner_queue"] else None,
            output_queue=scraper["output_queue"],
        )
        for scraper in scrapers
    ]

    for manager in managers:
        manager.start()

    # Monitor all scrapers
    try:
        while not stop_event.is_set():
            for manager in managers:
                if (
                    manager.scraper_thread
                    and not manager.scraper_thread.processed_queue.empty()
                ):
                    print(manager.scraper_thread.processed_queue.get())
            time.sleep(0.1)
    except KeyboardInterrupt:
        for manager in managers:
            manager.stop()
        print("All scrapers stopped.")

    finally:
        for manager in managers:
            manager.stop()
        print("All scrapers stopped.")


if __name__ == "__main__":
    URL = "https://pump.fun/advanced"  # Replace with your URL
    TABLE_XPATH = "/html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table"  # Replace with your table's XPath
    headers = [
        "coin name",
        "fullname",
        "bd",
        "mc",
        "vol",
        "t10",
        "holders",
        "age",
        "dh",
        "snipers",
        "address",
    ]
    headers_gmgn_1 = [
        "ticker",
        "name",
        "dev sold/bought",
        "age",
        "address",
        "liquidity",
        "total holders",
        "volume",
        "market cap",
        "full_address",
    ]
    # TRUMP    = name
    # THE ALMI
    # 0%
    # Run     = dev sold
    # Fkr7i...8tU = address
    # $0.0₅83176 = current price
    # 0%       = 24h
    # 0/1      = snipers
    # 0%       = bluechip
    # 0%      = top 10
    # Safe    = audit
    # 4/4
    headers_gmgn = [
        "ticker",
        "name",
        "i dont know",
        "dev sold?",
        "address",
        "current price",
        "24h",
        "snipers",
        "bluechip",
        "top 10",
        "audit",
        "full_address",
    ]

    extract_dynamic_table_data_2(columns=[headers_gmgn_1, headers_gmgn])

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


# def open_url_and_wait(url, wait_time=10):
#     # Setup WebDriver options
#     options = webdriver.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-dev-shm-usage")
#     options.headless = True  # Run in headless mode

#     # Initialize WebDriver
#     driver = webdriver.Chrome(options=options)

#     try:
#         # Open the URL
#         driver.get(url)
#         print(f"Opened URL: {url}")

#         # Wait for the page to load
#         ss = WebDriverWait(driver, wait_time).until(
#             EC.presence_of_element_located(
#                 (By.XPATH, "/html/body/div[4]/div[5]/button")
#             )
#         )
#         # ss.click()
#         driver.execute_script("arguments[0].click();", ss)
#         print("Page loaded successfully")

#         # Perform additional actions here if needed

#     except Exception as e:
#         print(f"An error occurred: {e}")

#     finally:
#         # Close the WebDriver
#         driver.quit()
#         print("WebDriver closed")


# if __name__ == "__main__":
#     URL = "https://pump.fun/advanced"  # Replace with your URL
#     open_url_and_wait(URL)
