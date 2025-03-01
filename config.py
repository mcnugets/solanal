from selenium.webdriver.common.by import By
from queue import Queue
from queue_manager import queue_manager


queue_m = queue_manager()

queue_m.add_queue(["gmgn", "gmgn2", "solscan"])
que = Queue()


driver_path = r"C:\Users\sulta\AppData\Local\Programs\Python\Python310\lib\site-packages\chromedriver_autoinstaller\133\chromedriver.exe"
configs = {
    "pumpfun": {
        "type": "pumpfun",
        "url": "https://pump.fun/advanced",
        "row_locator": (By.TAG_NAME, "tr"),
        "popup_locator": (By.XPATH, "/html/body/div[4]/div[5]/button"),
        "main_locator": (  # change main locator to pumfun
            By.XPATH,
            "/html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div",
        ),
        "driver_path": driver_path,
        "div_locator": (
            By.XPATH,
            " /html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table/tbody/tr[1]/td[1]",
        ),
    },
    "gmgn_2": {
        "type": "pumpfun",
        "url": "https://gmgn.ai/new-pair/tCkVIIwp?chain=sol",
        "row_locator": (By.CLASS_NAME, "g-table-row"),
        "popup_locator": (By.XPATH, "/html/body/div[3]/div/div[3]"),
        "main_locator": (
            By.XPATH,
            "/html/body/div[1]/div/div/main/div[2]/div/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div",
        ),
        "driver_path": driver_path,
    },
    "gmgn": {
        "type": "gmgn",
        "url": "https://gmgn.ai/sol/token/",
        "row_locator": (By.CLASS_NAME, "css-1jy8g2v"),
        "popup_locator": (By.XPATH, "/html/body/div[3]/div/div[3]"),
        "driver_path": driver_path,
        "main_locator": (By.CLASS_NAME, "css-1jy8g2v"),
        "csv_path": "pumpfun_data.csv",
        "input_queue": queue_m.get_queue("gmgn2")["output_queue"],
        "inner_queue": queue_m.get_queue("gmgn")["inner_queue"],
    },
    "solscan": {
        "type": "solscan",
        "url": "https://solscan.io/token/",
        "row_locator": (By.XPATH, "/html/body/div[3]/div[3]/button[2]"),
        "popup_locator": (),
        "driver_path": driver_path,
        "main_locator": (
            By.XPATH,
            "/html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/button",
        ),
        "csv_path": "pumpfun_data.csv",
        "download_path": "holders",
        "input_queue": queue_m.get_queue("gmgn")["output_queue"],
        "inner_queue": queue_m.get_queue("solscan")["inner_queue"],
    },
}

#  URL = "https://solscan.io/token/"
#     main_locator = (
#         By.XPATH,
#         "/html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/button",
#     )
#     row_locator = (By.XPATH, "/html/body/div[3]/div[3]/button[2]")
#     ss = solscan_processor(
#         main_locator=main_locator,
#         popup_locator=(),
#         row_locator=row_locator,
#         url=URL,
#         csv_path="../pumpfun_data.csv",
#         download_path="../holders",
#         driver_path=r"C:\Users\sulta\AppData\Local\Programs\Python\Python310\lib\site-packages\chromedriver_autoinstaller\131\chromedriver.exe",
#     )


# pumpfun_config = {
#     "type": "pumpfun",
#     "url": "https://pump.fun/advanced",
#     "row_locator": (By.TAG_NAME, "tr"),
#     "popup_locator": (By.XPATH, "/html/body/div[4]/div[5]/button"),
#     "main_locator": (  # change main locator to pumfun
#         By.XPATH,
#         "/html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div",
#     ),
#     "driver_path": driver_path,
#     "div_locator": (
#         By.XPATH,
#         " /html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table/tbody/tr[1]/td[1]",
#     ),
# }
# gmgn_config_2 = {
#     "type": "pumpfun",
#     "url": "https://gmgn.ai/new-pair/tCkVIIwp?chain=sol",
#     "row_locator": (By.CLASS_NAME, "g-table-row"),
#     "popup_locator": (By.XPATH, "/html/body/div[3]/div/div[3]"),
#     "main_locator": (
#         By.XPATH,
#         "/html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div",
#     ),
#     "driver_path": driver_path,
# }

# gmgn_config = {
#     "type": "gmgn",
#     "url": "https://gmgn.ai/sol/token/",
#     "row_locator": (By.CLASS_NAME, "css-1jy8g2v"),
#     "popup_locator": (By.XPATH, "/html/body/div[3]/div/div[3]"),
#     "driver_path": driver_path,
#     "main_locator": (By.CLASS_NAME, "css-1jy8g2v"),
#     "csv_path": "pumpfun_data.csv",
# }


CLEANING_PATTERNS = {
    r"\n+": "#",  # Replace newlines with hash
    r"#+": "#",  # Normalize multiple hashes
    r"^\#|\#$": "",  # Remove leading/trailing hashes
}
patterns = {
    "patterns_pumpfun": {
        "MC": "",  # Removes "MC"
        "Vol": "",  # Removes "Vol"
        "T10": "",  # Removes "T10"
        "DH": "",
    },
    "patterns_gmgn": {
        "24h": "",  # Removes "MC"
        "Snipers": "",  # Removes "Vol"
        "BlueChip": "",  # Removes "T10"
        "Top 10": "",
        "Audit": "",
        ">": "",
        "Safe": "",
        "Share": "",
    },
    "patterns_gmgn_2": {
        "Liq": "",  # Removes "MC"
        "Vol": "",  # Removes "Vol"
        r"\bV\b": "",
        r"\bMC\b": "",
    },
}
