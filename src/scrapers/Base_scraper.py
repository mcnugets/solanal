import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from undetected_chromedriver import ChromeOptions
import undetected_chromedriver as uc
import time
from pathlib import Path
import os
from colorama import init, Fore, Back, Style
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchWindowException,
)
from typing import Tuple, Literal, Annotated, Optional, List, Any, Union
from collections import deque
from selenium.webdriver.common.by import By as LocatorType
import logging
from abc import abstractmethod
from pydantic import BaseModel
from src.data.models import Address_Data as ad
import chromedriver_autoinstaller
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth

# "https://gmgn.ai/sol/token/"
#  "/html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table/tbody"
class Base_scraper:

    def __init__(
        self,
        driver_path: str,
        main_locator: Tuple[LocatorType, str],
        popup_locator: Tuple[LocatorType, str],
        row_locator: Tuple[LocatorType, str],
        url: str,
        download_path: str = "",
        extra_locator: Optional[Tuple[LocatorType, str]] = None,
    ):
        self.url = url
        # self.csv_path = csv_path
        self.driver = None
        self.driver_path = os.path.abspath(driver_path)
        self.download_path = download_path
        self.options = ChromeOptions()
        self.setup_driver()

        self.main_locator = main_locator
        self.popup_locator = popup_locator
        self.row_locator = row_locator
        self.extra_locator = extra_locator

        self.__deque = deque(maxlen=100)
        # self.__deque = TrackedDeque(
        #     maxlen=100,
        #     on_change=self._on_deque_change,
        #     validate=self._validate_deque_item,
        # )

    @property
    def _deque(self) -> deque:
        return self.__deque

    @_deque.setter
    def _deque(self, value: deque):
        """
        Set the deque value with validation

        Args:
            value: New deque value (deque or list of tuples)
        """
        if isinstance(value, deque):
            self._deque = value
        elif isinstance(value, list):
            new_deque = deque(maxlen=self._deque.maxlen)
            for item in value:
                if isinstance(item, tuple) and len(item) == 2:
                    new_deque.append(item)
                else:
                    raise ValueError(f"Invalid item in list: {item}")
            self._deque = new_deque
        else:
            raise TypeError(f"Invalid deque type: {type(value)}")

    def pre_scraping_hook(self):
        """Hook to run before the loop starts. Default: do nothing."""
        pass

    def in_loop_hook(self):
        """Hook to run inside the loop. Default: do nothing."""
        pass

    def setup_website(self):
        pass

    @abstractmethod
    def _scrape_data(self) -> ad | None:
        pass

    # TODO: future note to myself: create pydantic model for the data
    def validate_unprocessed(
        self, address: str | None = None, data: List | str | None = None
    ) -> ad:
        return ad(address=address, data=data)

    def setup_driver(self):
        try:

            # options.add_argument("--headless")

            # Proper headless setup for undetected-chromedriver
            self.options.add_argument("--headless=new")  # Use new headless mode
            self.options.add_argument("--disable-blink-features=AutomationControlled")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--disable-dev-shm-usage")
            self.options.add_argument("--window-size=1920,1080")
            self.options.add_argument("--disable-popup-blocking")
            self.options.add_argument("--incognito")
            # self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
            # self.options.add_experimental_option("useAutomationExtension", False)

            # Additional required arguments for headless
            self.options.add_argument("--start-maximized")
            self.options.add_argument("--enable-javascript")
            self.options.add_argument("--disable-blink-features")
            self.options.add_argument("--disable-notifications")

            self.options.add_argument(
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.114  Safari/537.36"
            )

            if self.download_path:
                prefs = {
                    "download.default_directory": os.path.abspath(self.download_path),
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True,
                }
                self.options.add_argument("--disable-popup-blocking")

                self.options.add_experimental_option("prefs", prefs)
            # chromedriver_autoinstaller.install()
            self.driver = uc.Chrome(
                options=self.options,
                version_main=135,
                driver_executable_path=self.driver_path,
            )
            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Linux x86_64",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True
            )


            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Driver setup failed: {e}")
            return False

    def _get_element(
        self,
        locator: Annotated[
            Tuple[LocatorType, str],
            {
                "description": "Tuple containing locator type and selector string for main element"
            },
        ],
        wait_time: int = 10,
    ):

        try:
            time.sleep(5)
            # Wait for data to load
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located(locator)
            )

            return element
        except Exception as e:
            print(f"Error loading element: {e}")
            logging.error(f"An error occurred during website setup: {e}")
            return None

    def handle_popup(self):
        if not self.popup_locator:
            return
        try:
            popup = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.popup_locator)
            )

            if popup:
                self.driver.execute_script("arguments[0].click();", popup)

                print("Popup closed successfully")
        except StaleElementReferenceException:
            attempts += 1
            print(f"Stale element encountered, re-locating... Attempt {attempts}")

        except Exception as e:
            logging.error(f"Error closing popup: {e}")

    def handle_extra(self):
        try:
            popup_el = self._get_element(self.extra_locator, wait_time=5)

            if not popup_el:
                return
            size = self.driver.get_window_size()
            width, height = size["width"], size["height"]
            # 533
            # 198
            x = width / 3
            y = height / 3

            body = self.driver.find_element(By.TAG_NAME, "body")
            ActionChains(self.driver).move_to_element_with_offset(
                popup_el, x, y
            ).click().perform()
        except Exception as e:
            logging.error(f"Error performing random click in handle_extra: {e}")

    def load_html_element(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                # (By.XPATH, self.table_xpath)
                EC.presence_of_element_located(self.main_locator)
            )

            return element
        except Exception as e:
            print(f"Error loading element: {e}")
            logging.error(f"An error occurred during website setup: {e}")
            return None

    def fetch_url(self, address=""):
        try:
            url = f"{self.url}{address}"

            self.driver.get(url)
            time.sleep(random.uniform(2, 5)) 
        except Exception as e:
            print(f"Error fetching URL: {e}")

    def cleanup(self):
        if self.driver:
            self.driver.quit()


# Usage
# if __name__ == "__main__":
#     driver_path = r"C:\Users\sulta\AppData\Local\Programs\Python\Python310\lib\site-packages\chromedriver_autoinstaller\131\chromedriver.exe"
#     driver_path = driver_path.replace("\\", "/")

#     # Method 2: Using Path object
#     driver_path = str(Path(driver_path).as_posix())

#     gmgn_config = {
#         "URL": "https://gmgn.ai/sol/token/",
#         "row_locator": (By.CLASS_NAME, "css-1jy8g2v"),
#         "popup_locator": (By.XPATH, "/html/body/div[3]/div/div[3]"),
#         "driver_path": r"C:\Users\sulta\AppData\Local\Programs\Python\Python310\lib\site-packages\chromedriver_autoinstaller\131\chromedriver.exe",
#         "main_locator": (By.CLASS_NAME, "css-1jy8g2v"),
#         "csv_path": "pumpfun_data.csv",
#     }

#     gmgn_scraper = gmgn_processor(
#         url=gmgn_config["URL"],
#         driver_path=gmgn_config["driver_path"],
#         main_locator=gmgn_config["main_locator"],
#         row_locator=gmgn_config["row_locator"],
#         popup_locator=gmgn_config["popup_locator"],
#         csv_path=gmgn_config["csv_path"],
#     )

#     gmgn_scraper._scrape_data()
