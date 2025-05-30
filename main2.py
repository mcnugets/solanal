import logging
from typing import List, Optional
from selenium.webdriver.common.by import By
from collections import deque
from threading import Event

import signal
import time
from selenium.webdriver.support import expected_conditions as EC
from src.core.config import queue_m
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from src.thread_related.factories.threader_factory import threader_factory
from src.core.config import CONFIG, SCRAPERS, SCRAPER_CONFIGS, GLOBAL_CONFIG
from src import (
    DataCompiler,
    Scraper_Manager,
    ScraperLogger,
    gmgn_processor,
    solscan_processor,
    pumpfun_processor,
    llm_threader,
    llm_analyser,
    llm_data_processor,
    validate_sources,
)
from src.DataFrameManager import DataFrameManager
from src.thread_related.distributor import dsitributor
from queue import Queue
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


# def signal_handler(sig, frame):
#     global stop_event
#     print("\nShutting down gracefully...")
#     stop_event.set()


# signal.signal(signal.SIGINT, signal_handler)
# stop_event = Event()


def extract_dynamic_table_data_2(columns: List[str] = None):
    global stop_event
    shared_state_ = {"current turn": SCRAPER_CONFIGS["gmgn_2"]["type"]}

    manager_ = Scraper_Manager(logger=logger, shared_state=shared_state_)
    for scraper in SCRAPER_CONFIGS:
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
            GLOBAL_CONFIG["data_sources"][0]: queue_m.get_queue(
                GLOBAL_CONFIG["data_sources"][0]
            )["output_queue"],
            GLOBAL_CONFIG["data_sources"][1]: queue_m.get_queue(
                GLOBAL_CONFIG["data_sources"][1]
            )["output_queue"],
            GLOBAL_CONFIG["data_sources"][2]: queue_m.get_queue(
                GLOBAL_CONFIG["data_sources"][2]
            )["output_queue"],
        },
        output_queue=queue_m.get_queue("compiled")["output_queue"],
        logger=logger,
        data_sources=validate_sources(
            pumpfun=GLOBAL_CONFIG["data_sources"][0],
            holders=GLOBAL_CONFIG["data_sources"][2],
        ),
    )
    compiler.start()

    #
    #
    # model_name = "deepseek-r1:7b"
    # data_setup_llm = llm_data_processor(logger=logger)
    # llm_data_analysis_input = llm_analyser(
    #     model=model_name,
    #     logger=logger,
    #     llm_data_processor=data_setup_llm,
    # )
    # llm_dataflow_manager = llm_threader(
    #     input_queue=queue_m.get_queue("compiled")["output_queue"],
    #     logger=logger,
    #     llm_anal=llm_data_analysis_input,
    # )
    # llm_dataflow_manager.start_all()

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


def orchestrator(scrape_manager: Scraper_Manager):

    topic = "gmgn_2" # central point of our distributor
    distributor = dsitributor(logger=logger)
    gmgn_2_output_queue = queue_m.get_queue("gmgn_2")["output_queue"]
    # gmgn_output_queue = queue_m.get_queue("gmgn")["output_queue"]
    solscan_output_queue = queue_m.get_queue("holders")["output_queue"]


    to_solscan_scraper = Queue()

    fac = threader_factory()
    gmgn_two = fac.create_threader(
        threader_type="scrapers",
        scraper_type="gmgn_2",
        configs=CONFIG,
        distributor=distributor,
        topic=topic
    )

    # gmgn_one = fac.create_threader(
    #     threader_type="scrapers",
    #     scraper_type="gmgn",
    #     configs=CONFIG,
    #     output_queue=gmgn_output_queue,
    #     input_queue=gmgn_2_output_queue,
    # )

    solscan = fac.create_threader(
        threader_type="scrapers",
        scraper_type="solscan",
        configs=CONFIG,
        input_queue=gmgn_2_output_queue,
        output_queue=solscan_output_queue,
        distributor=distributor,
        topic=topic
    )

    datacompiler = fac.create_data_compiler(configs=CONFIG['global'], distributor=distributor, topic=topic)
  
    scrape_manager.add_scraper_v2(solscan)
    datacompiler.start()
 
    scrape_manager.add_scraper_v2(gmgn_two)
    # scrape_manager.add_scraper_v2(gmgn_one)
    scrape_manager.start()
    
    final = queue_m.get_queue('compiled').get('output_queue')
    while True:
        time.sleep(5)
        if not final.empty():
            data = final.get()
            print("\n--- Final Compiled Data ---")
            print(f"Queue size: {final.qsize()}")
            print("Data contents:")
            if hasattr(data, 'model_dump'):  # Check if it's a Pydantic model
                for field, value in data.model_dump().items():
                    print(f"{field}: {value}")
            else:
                print(data)
            print("--------------------------\n")



gmgn = [
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

gmgn_2 = [
        "ticker",
        "name",
        "age",       
        "address",
        "liquidity",
        "total holders",
        "volume",
        "market cap",
        "Top 10",
        "Dev holds",
        "insiders",
        "snipers"
        "rug"
        "full_address",
    ]

# BichiBichi30m Cf7Gk...onk Liq$51.8K64038V$514.2KMC$135.8K20% 0.3% snipers3 rug7% delete this: Buy
data_sample = [
    "6p8ez...Aq4",
    "$0.0000",
    "--%",
    "3/4",
    "0%",
    "0.4%",
    "4/4",
    "1%",
    "6p8ez2tKSKhyCZpv29sxd5fwpzS6uDpW515hUybvSAq4",
]
data_sample_2 = [
    "11cfd...ebp",
    "$0.0000",
    "--%",
    "--",
    "0%",
    "Audit",
    "11cfd6acd78d06c7c555f91a427e9d10.webp",
]
data_sample_3 = ['0x', '0xa', '0xa', 'Buy', '1s', 'Gq7XD...oop', '$0', '--', '$0', '$0', 'Gq7XDXZ3ZYxfXHbpbtRsL5S7EmiwpW68vn1BKrQboop']
data_sample_4 = ['0xa', '0xa', 'Buy', '1s', 'Gq7XD...oop', '$0', '--', '$0', '$0', 'Gq7XDXZ3ZYxfXHbpbtRsL5S7EmiwpW68vn1BKrQboop']
data_sample_5 = ['0xa', '0xa', 'Buy', '1s', 'Gq7XD...oop', '$0', '--','5%', '$0', '$0', 'Gq7XDXZ3ZYxfXHbpbtRsL5S7EmiwpW68vn1BKrQboop']
data_sampel_6 = ['0x','0xa', '0xa', 'Buy', '1s', 'Gq7XD...oop', '$0', '--','5%', '$0', '$0', 'Gq7XDXZ3ZYxfXHbpbtRsL5S7EmiwpW68vn1BKrQboop']

data_sample_7 = ['GTAVI', 'Grand Trump Auto VI', '1%', 'HODL', 'Bmpj9...XAS', '$0.0₅43362', '-2.23%', '--', '0%', '8.3%', '4/4', '1%', 'Bmpj9ghk4ZFVYDVp46R243guddHtDQYWXx96FHW9rXAS']

data_sample_8 = ['ETH', 'dont buy this shit', '25%', 'HODL', 'bPeYd...ump', '$0.0₅61682', '+38.02%', '--', '0%', '6.2%', '4/4', '1%', 'bPeYdx2xJthrk8E3nPH5aqHmY43rF9xaocRhFRtpump']

data_sample_9 = ['TiedIguana', 'TiedIguana', '3%', 'Run', '8uJeC...ump', '$0.0₅44040', '+1.59%', '4/8', '0%', '0.5%', '4/4', '1%', '8uJeCFBzGD4qxAP46giPqKJnL9R95jQmJTLRhnkXpump'] 

def test_case():
    """Main function for testing DataFrameManager functionality."""
    import pandas as pd
    
    
    # Initialize DataFrameManager with test columns
    test_columns = ["ticker", "name", "address", "liquidity", "market_cap"]

    df_manager = DataFrameManager(columns=gmgn_2, base_file="pumpfun_data.csv", logger=logger)
    
    ans = df_manager.process_data(data_sample_3)
    print(ans)#
    print("---------------------")
    ans_2 = df_manager.process_data(data_sample_4)
    print(ans_2)
    print("=====================")
    ans_3 = df_manager.process_data(data_sample_5)
    print(ans_3)


    df_manager = DataFrameManager(columns=gmgn, base_file="gmgn_data.csv", logger=logger)
    ans5 = df_manager.process_data(data_sample_7)
    print(ans5)


    print(df_manager.process_data(data_sample_8))


    print(df_manager.process_data(data_sample_9))


def test_case_pumpfun():
    from src.scrapers.playwright.pumpfun_scraper import pumpfun_scraper
    from src.core.logger import ScraperLogger as log
    table_xpath = '/html/body/div[1]/div[2]/div[1]/main/div[2]/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div/div/div/div'

    logger = log()  # Initialize logger if not already available
    pumpfun_scraper_instance = pumpfun_scraper(
        url="https://gmgn.ai/new-pair/tCkVIIwp?chain=sol&tab=home",
        logger=logger,
        main_locator=table_xpath,
        row_locator="div",
        popup_locator="/html/body/div[2]/div[1]/div[3]"
    )

    # try:
    while True:
        result =  pumpfun_scraper_instance.start_scrape()
        boom = next(result)
        print(boom)

    # except StopIteration:
    #     print("No more data to scrape")


 
   
    



if __name__ == "__main__":
    # URL = "https://pump.fun/advanced"  # Replace with your URL
    # TABLE_XPATH = "/html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table"  # Replace with your table's XPath

    # extract_dynamic_table_data_2(
    #     columns=[COLUMN_HEADERS["gmgn_2"], COLUMN_HEADERS["gmgn"]]
    # )
 
        
    
    manager_ = Scraper_Manager(logger=logger)
    orchestrator(manager_)

    # test_case_pumpfun()

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
