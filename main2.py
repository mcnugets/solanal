import logging
from typing import List, Optional
from selenium.webdriver.common.by import By
from collections import deque
from threading import Event

import signal
import time
from selenium.webdriver.support import expected_conditions as EC
from config import CLEANING_PATTERNS, configs, patterns, queue_m
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

from src import (
    DataCompiler,
    Scraper_Manager,
    ScraperLogger,
    gmgn_processor,
    solscan_processor,
    pumpfun_processor,
)

logger = ScraperLogger()

# TODO: things fo configer:
# TODO: use configs to set params
# TODO: better error handling
# TODO: add extra params: every what row to save,
# TODO: set the batches to process
# TODO: better logging output

# TODO: add web scraper to bubblemaps
# TODO: add web scraper to solsniffer
# TODO: add analyser code for twitter, and  tg


#  TODO: create config file
#  TODO: create pydantic models for validation


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
    shared_state_ = {"current turn": gmgn_2_config["type"]}

    scrapers = [
        {
            "config": gmgn_2_config,
            "columns": columns[0],
            "patterns": patterns["patterns_gmgn_2"],
            "cleaning_patterns": CLEANING_PATTERNS,
            "base_file": "pumpfun_data.csv",
            "input_queue": None,
            "output_queue": queue_m.get_queue("gmgn2")["output_queue"],
        },
        # {
        #     "config": gmgn_config,
        #     "columns": columns[1],
        #     "patterns": patterns["patterns_gmgn"],
        #     "cleaning_patterns": CLEANING_PATTERNS,
        #     "base_file": "gmgn_data.csv",
        #     "input_queue": queue_m.get_queue("gmgn2")["output_queue"],
        #     "output_queue": queue_m.get_queue("gmgn")["output_queue"],
        # },
        {
            "config": solscan_config,
            "columns": "",
            "patterns": "",
            "cleaning_patterns": "",
            "base_file": "",
            "input_queue": queue_m.get_queue("gmgn2")["output_queue"],
            "output_queue": queue_m.get_queue("solscan")["output_queue"],
        },
    ]

    manager_ = Scraper_Manager(logger=logger, shared_state=shared_state_)
    for scraper in scrapers:
        manager_.add_scraper(
            config=scraper["config"],
            columns=scraper["columns"],
            patterns=scraper["patterns"],
            cleaning_patterns=scraper["cleaning_patterns"],
            base_file=scraper["base_file"],
            input_queue=(scraper["input_queue"] if scraper["input_queue"] else None),
            output_queue=scraper["output_queue"],
        )

    try:
        manager_.start_all()
    except KeyboardInterrupt:

        manager_.stop_all()
        print("All scrapers stopped.")

    finally:
        # manager_.stop_all()
        print("All scrapers stopped.")
    compiler = DataCompiler(
        input_queues={
            "gmgn2": queue_m.get_queue("gmgn2")["output_queue"],
            "gmgn": queue_m.get_queue("gmgn")["output_queue"],
            "solscan": queue_m.get_queue("solscan")["output_queue"],
        },
        output_queue=queue_m.get_queue("compiled")["output_queue"],
        logger=logger,
    )

    compiler.start()

    # Monitor all scrapers
    # try:
    #     while not stop_event.is_set():
    #         for manager in managers:
    #             if (
    #                 manager.scraper_thread
    #                 and not manager.scraper_thread.processed_queue.empty()
    #             ):
    #                 print(manager.scraper_thread.processed_queue.get())

    #         if not queue_m.get_queue("compiled")["output_queue"].empty():
    #             compiled_data = queue_m.get_queue("compiled")["output_queue"].get()
    #             print(f"Compiled data: {compiled_data}")
    #             queue_m.get_queue("final")["output_queue"].put(compiled_data)
    #             logging.info(
    #                 f'---INFO The final queue size: {queue_m.get_queue("final")["output_queue"].qsize()}'
    #             )
    #         time.sleep(0.1)

    # except KeyboardInterrupt:
    #     for manager in managers:
    #         manager.stop()
    #     print("All scrapers stopped.")

    # finally:
    #     for manager in managers:
    #         manager.stop()
    #     print("All scrapers stopped.")


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
        "Taxes",
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
