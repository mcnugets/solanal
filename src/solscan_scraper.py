from src.Base_scraper import Base_scraper, CSVLoaderMixin
from typing import Annotated, Tuple
from selenium.webdriver.common.by import By as LocatorType
from collections import deque
import os
import logging
import time
import pandas as pd
import undetected_chromedriver as uc
import tempfile
from selenium.webdriver.common.by import By
from pathlib import Path


class solscan_processor(Base_scraper, CSVLoaderMixin):

    def __init__(
        self,
        driver_path,
        main_locator,
        popup_locator,
        row_locator,
        url,
        csv_path,
        download_path,
        input_queue,
        inner_queue,
    ):
        self.csv_path = csv_path

        super().__init__(
            driver_path,
            main_locator,
            popup_locator,
            row_locator,
            url,
            download_path=download_path,
        )
        self.deque = deque(maxlen=100)
        self.input_queue = input_queue
        self.inner_queue = inner_queue

        # self.setup_driver()

    # xpath /html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/button/div
    # https://solscan.io/token/
    def _scrape_data(self):
        self.load_csv_to_deque()

        while self.deque:

            address = self.deque.pop()
            print(f"checking the token address: {address}")
            self.fetch_url(address + r"#holders")
            try:
                time.sleep(2)
                self.handle_csv_download(address)

                logging.info(f"Fetched data for {address}")

            except Exception as e:
                logging.error(f"Error fetching {address}: {e}")
                # continue

    def handle_csv_download(self, address):
        try:
            csv_button = self._get_element(locator=self.main_locator)
            if csv_button:
                csv_button.click()
                # self.driver.execute_script("arguments[0].click();", csv_button)
                # /html/body/div[3]/div[3]/button[2]
                confirm_buttton = self._get_element(locator=self.row_locator)
                if confirm_buttton:
                    confirm_buttton.click()
                    downdload_file = self.wait_for_download()
                    print(f"downloadedd file {downdload_file}")
                    if downdload_file:
                        custom_path = Path(downdload_file)
                        new_name = f"{address}_data.csv"
                        self.rename_file_with_retry(custom_path, new_name)
                        print("file rename success")
                        logging.info(f"Downloaded file renamed to {custom_path}")
        except Exception as err:
            logging.error(f"Error: {err}")
            print(f"Error: {err}")

    def wait_for_download(self, timeout=15):
        end_time = time.time() + timeout
        while time.time() < end_time:
            downloaded_file = Path(self.download_path)
            latest_file = max(
                downloaded_file.glob("*"), key=lambda f: f.stat().st_ctime, default=None
            )
            return latest_file

            time.sleep(1)
        logging.error("Download timed out")
        return None

    def handle_popup(self):
        pass

    def rename_file_with_retry(self, src: Path, dst, retries=5, delay=1):
        for _ in range(retries):
            try:
                new_name = src.with_name(dst)
                src.rename(new_name)
                return
            except PermissionError as e:
                if e.winerror == 32:  # File is being used by another process
                    logging.warning(f"File is in use, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
        logging.error(f"Failed to rename file after {retries} retries")


if __name__ == "__main__":
    URL = "https://solscan.io/token/"
    main_locator = (
        By.XPATH,
        "/html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/button",
    )
    row_locator = (By.XPATH, "/html/body/div[3]/div[3]/button[2]")
    ss = solscan_processor(
        main_locator=main_locator,
        popup_locator=(),
        row_locator=row_locator,
        url=URL,
        csv_path="../pumpfun_data.csv",
        download_path="../holders",
        driver_path=r"C:\Users\sulta\AppData\Local\Programs\Python\Python310\lib\site-packages\chromedriver_autoinstaller\131\chromedriver.exe",
    )
    ss._scrape_data()
