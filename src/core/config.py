from selenium.webdriver.common.by import By
from queue import Queue
from src.data.models import Pair_data
from src.thread_related.queue_manager import queue_manager

GLOBAL_CONFIG = {
    # "driver_path": "/usr/bin/chromedriver",
    "data_sources": ["gmgn_2", "holders"],
    "cleaning_patterns": {
        r"\n+": "#",  # Replace newlines with hash
        r"#+": "#",  # Normalize multiple hashes
        r"^\#|\#$": "",  # Remove leading/trailing hashes
    },
}


queue_m = queue_manager()

queue_m.add_queue(GLOBAL_CONFIG["data_sources"])
queue_m.add_queue("to_holders")
queue_m.add_queue(["compiled", "final"])  # Add new queue for compiled data

# incorporate DATA_SOURCES into configs but later
SCRAPER_CONFIGS = {
    "pumpfun": {
        "type": "pumpfun",
        "url": "https://pump.fun/advanced",
        "row_locator": (By.TAG_NAME, "tr"),
        "popup_locator": (By.XPATH, "/html/body/div[4]/div[5]/button"),
        "main_locator": (  # change main locator to pumfun
            By.XPATH,
            "/html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div",
        ),
        # "driver_path": GLOBAL_CONFIG["driver_path"],
        "div_locator": (
            By.XPATH,
            "/html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table/tbody/tr[1]/td[1]",
        ),
    },
    "gmgn_2": {
        "type": "gmgn_2",
        "url": "https://gmgn.ai/new-pair/tCkVIIwp?chain=sol",
        "row_locator": (By.TAG_NAME, "div"),
        # /html/body/div[1]/div[2]/div[1]/main/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[1]/div
        # <div>
        # /html/body/div[1]/div[2]/div[1]/main/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div/div/div/div/div[2]
        # //*[@id="tabs-:r1ke:--tabpanel-0"]/div/div[1]/div[2]/div/div/div/div/div/div[1]
        "popup_locator": (By.XPATH, "/html/body/div[2]/div/div[3]"),
        "main_locator": (
            By.XPATH,
            "/html/body/div[1]/div[2]/div[1]/main/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div/div/div/div",
        ),
        # "driver_path": GLOBAL_CONFIG["driver_path"],
        "extra_locator": (
            By.XPATH,
            "/html/body/div[4]/div/div[2]/div",
        ),
    },
    "gmgn": {
        "type": "gmgn",
        "url": "https://gmgn.ai/sol/token/",
        "row_locator": (
            By.XPATH,
            "/html/body/div[1]/div[2]/div[1]/main/div/div[2]/div[1]",
        ),
        "popup_locator": (By.XPATH, "/html/body/div[2]/div/div[3]"),
        # "driver_path": GLOBAL_CONFIG["driver_path"],
        "main_locator": (By.CLASS_NAME, "css-1jy8g2v"),
        "csv_path": "pumpfun_data.csv",
    },
    "solscan": {
        "type": "solscan",
        "url": "https://solscan.io/token/",
        "row_locator": (By.XPATH, "/html/body/div[3]/div[3]/button[2]"),
        "popup_locator": (),
        # "driver_path": GLOBAL_CONFIG["driver_path"],
        "main_locator": (
            By.XPATH,
            "/html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/div[2]/button[2]",
            
        ),
        "csv_path": "pumpfun_data.csv",
        "download_path": "holders",
    },
}
# row_locator = f'xpath=/html/body/div[1]/div[2]/div[1]/main/div[2]/div/div[2]/div[1]'
#         # 7. Find the element on the page that contains the text we want.
#         # We use page.locator() with a CSS selector.
#         # For example.com, the main heading is inside an <h1> tag.
#         # The main paragraph is inside a <p> tag.

#         # Find the locator for the <h1> element
#         popup_xpath = "/html/body/div[2]/div[1]/div[3]"
#         # css-1r20knq
#         page.wait_for_selector(f'xpath={popup_xpath}')
#         page.locator(f'xpath={popup_xpath}').click()
#         table_xpath = f'xpath=/html/body/div[1]/div[2]/div[1]/main/div[2]/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div'
        
SCRAPER_CONFIGS_2 = {
    "pumpfun": {
        "type": "pumpfun",
        "url": "https://pump.fun/advanced",
        "row_locator": "tr",
        "popup_locator": "/html/body/div[4]/div[5]/button",
        "main_locator": "/html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div",
        # "driver_path": GLOBAL_CONFIG["driver_path"],
        "div_locator": "/html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table/tbody/tr[1]/td[1]",
    },
    # use this for further development where we insert class attributes into optional
    # so that we can identify labels taht are not consistent
    #     "gmgn_2": {
    #     "type": "gmgn_2",
    #     "url": "https://gmgn.ai/new-pair/tCkVIIwp?chain=sol&tab=home",
    #     "row_locator": "div",
    #     "popup_locator": "/html/body/div[2]/div[1]/div[3]",
    #     "main_locator": "/html/body/div[1]/div[2]/div[1]/main/div[2]/div/div/div[2]/div[1]/div/div[1]/div[2]/div/div/div/div/div",
    #     # "driver_path": GLOBAL_CONFIG["driver_path"],
    #     "extra_locator": "/html/body/div[4]/div/div[2]/div",
    #     # "optional":[]
    # },
    "gmgn_2": {
        "type": "gmgn_2",
        "url": "https://gmgn.ai/?launchpad=pump&chain=sol&ref=tCkVIIwp&tab=new_creation",
        "row_locator": "div",
        "popup_locator": "/html/body/div[2]/div[1]/div[3]",
        "main_locator": "/html/body/div[1]/div[2]/div[1]/main/div[2]/main/div[2]/div/div[1]/div[2]/div/div/div/div/div",
        # "driver_path": GLOBAL_CONFIG["driver_path"],
        "extra_locator": "/html/body/div[4]/div/div[2]/div",
    },
    "gmgn": {
        "type": "gmgn",
        "url": "https://gmgn.ai/sol/token/",
        "row_locator": "/html/body/div[1]/div[2]/div[1]/main/div[2]/div/div[2]/div[1]",
        "popup_locator": "/html/body/div[2]/div[1]/div[3]",
        # "driver_path": GLOBAL_CONFIG["driver_path"],
        "main_locator": "css-1jy8g2v",
        "csv_path": "pumpfun_data.csv",
    },
    "solscan": {
        "type": "solscan",
        "url": "https://solscan.io/token/",
        "row_locator": "/html/body/div[3]/div[3]/button[2]",
        "popup_locator": "",
        # "driver_path": GLOBAL_CONFIG["driver_path"],
        "main_locator": "/html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/div[2]/button[2]",
        "csv_path": "pumpfun_data.csv",
        "download_path": "holders",
    },
}



PATTERNS = {
    "pumpfun": [
        "MC",
        "Vol",
        "T10",
        "DH",
    ],
    "gmgn": [
        "24h",
        "Snipers",
        "BlueChip",
        "Name",
        "CA",
        "Top 10",
        "Audit",
        ">",
        "Safe",
        "Share",
        "Taxes",
        "Dex",
    ],
    "gmgn_2": [
       "Liq",
        "Vol",
        "?",
        "V",
        "MC",
        "Buy",
        "TX"
    ],
}

COLUMN_HEADERS = {
    "pumpfun": [
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
    ],
    "gmgn": [
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
    ],
    #   "gmgn_2": [
    #     "ticker",
    #     "name",
    #     "dev sold/bought",
    #     "age",
    #     "address",
    #     "liquidity",
    #     "total holders",
    #     "volume",
    #     "market cap",
    #     "full_address",
    # ],
    # we'll keep the labels below for future when well deal with optional labels
#   gmgn_2 = [
#         "ticker",
#         "name",
#         "age",       
#         "address",
#         "liquidity",
#         "total holders",
#         "volume",
#         "market cap",
#         "Top 10",
#         "Dev holds",
#         "insiders",
#         "snipers"
#         "rug"
#         "full_address",
#     ]

    # "gmgn_2": [
    #     "ticker",
    #     "name",
    #     "age",
    #     "address",
    #     "migrated",
    #     "total holders",
    #     "TX",
    #     "status",
    #      "Top 10",
    #     "Dev holds",
    #     "insiders",
    #     "snipers"
    #     "rug"
    #     "volume",
    #     "market cap",
    #     "full_address",
    # ],
    # "gmgn_2": [
    #     "ticker",
    #     "name",
    #     "age",
    #     "address",
    #     "migrated",
    #     "total holders",
    #     "TX",
    #     "volume",
    #     "market cap",
    #     "full_address",
    # ],
        "gmgn_2": [
        "ticker",
        "name",
        "age",
        "address",
        "volume",
        "market cap",
        "total holders",
        "full_address",
    ],
}

# "gmgn_2": [
#         "ticker",
#         "name",
#         "age",
#         "address",
#         "liquidity",
#         "total holders",
#         "volume",
#         "market cap",
#         "full_address",
#     ],
# }

# -------------SETUP FOR OLD LOGIC
SCRAPERS = [
    {
        "name": "gmgn_2",
        "config": SCRAPER_CONFIGS["gmgn_2"],
        "columns": COLUMN_HEADERS["gmgn_2"],
        "patterns": PATTERNS["gmgn_2"],
        "cleaning_patterns": GLOBAL_CONFIG["cleaning_patterns"],
        "base_file": "pumpfun_data.csv",
        "input_queue": None,
        "output_queue": queue_m.get_queue(GLOBAL_CONFIG["data_sources"][0])[
            "output_queue"
        ],
    },
    # {
    #     "name": "gmgn",
    #     "config": SCRAPER_CONFIGS["gmgn"],
    #     "columns": COLUMN_HEADERS["gmgn"],
    #     "patterns": PATTERNS["gmgn"],
    #     "cleaning_patterns": GLOBAL_CONFIG["cleaning_patterns"],
    #     "base_file": "gmgn_data.csv",
    #     "input_queue": queue_m.get_queue(GLOBAL_CONFIG["data_sources"][0])[
    #         "output_queue"
    #     ],
    #     "output_queue": queue_m.get_queue(GLOBAL_CONFIG["data_sources"][1])[
    #         "output_queue"
    #     ],
    # },
    # {
    #     "name": "solscan",
    #     "config": SCRAPER_CONFIGS["solscan"],
    #     "columns": "",
    #     "patterns": "",
    #     "cleaning_patterns": "",
    #     "base_file": "",
    #     "input_queue": queue_m.get_queue(GLOBAL_CONFIG["data_sources"][0])[
    #         "output_queue"
    #     ],
    #     "output_queue": queue_m.get_queue(GLOBAL_CONFIG["data_sources"][2])[
    #         "output_queue"
    #     ],
    # },
]


# -------------FOR NEW CODE--------
# CENTRALISED APPROACH

THREADER_TYPE = ["scrapers", "llm"]
# CONFIG = {"global": GLOBAL_CONFIG, "scrapers": {}, "llm": {}}

CONFIG = {
    # Global settings (shared across all scrapers)
    "global": GLOBAL_CONFIG,
    # Scraper-specific configurations
    "scrapers": {
        "pumpfun": {
            "scraper": True,
            "wait": False,
            "save": True,
            "process": True,
            # Processor requirements (passed to pumpfun_processor)
            "scraper_configs": SCRAPER_CONFIGS_2["pumpfun"],
            # Data processing rules
            "columns": COLUMN_HEADERS["pumpfun"],
            "patterns": PATTERNS["pumpfun"],
            "base_file": "pumpfun_data.csv",
            "input_queue": None,
        },
        "gmgn_2": {
            "scraper": True,
            "wait": False,
            "save": True,
            "process": True,
            "scraper_configs": SCRAPER_CONFIGS_2["gmgn_2"],
            "columns": COLUMN_HEADERS["gmgn_2"],
            "patterns": PATTERNS["gmgn_2"],
            "base_file": "pumpfun_data.csv",
            "input_queue": None,
            "output_queue": None
        },
        "gmgn": {
            "scraper": True,
            "wait": True,
            "save": True,
            "process": True,
            "scraper_configs": SCRAPER_CONFIGS_2["gmgn"],
            "columns": COLUMN_HEADERS["gmgn"],
            "patterns": PATTERNS["gmgn"],
            "base_file": "gmgn_data.csv",
            "input_queue": "gmgn_2",  # Input queue changes depending on is predecessing operation type
            "output_queue": "gmgn"
        },
        "holders": {
            "scraper": True,
            "wait": True,
            "save": True,
            "process": False,
            "scraper_configs": SCRAPER_CONFIGS_2["solscan"],
            "columns": [],
            "patterns": {},
            "base_file": "",
            "input_queue": "to_holders",
            "output_queue": "holders"
        },
    },
    "llm": {
        "batch": 1,
        "model": "deepseek-r1:7b",
        "input_queue": "compiled",
        "output_queue": "final"
    },
}
