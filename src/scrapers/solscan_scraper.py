from .Base_scraper import Base_scraper
from typing import Annotated, Tuple, List
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

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchWindowException,
)
import asyncio

# import aiohttp


class solscan_processor(Base_scraper):

    def __init__(
        self,
        driver_path,
        main_locator,
        popup_locator,
        row_locator,
        url,
        csv_path,
        download_path,
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

        # self.setup_driver()

    # xpath /html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/button/div
    # https://solscan.io/token/
    def _scrape_data(self):
        # self.load_csv_to_deque()

        while len(self._deque) > 0:
            logging.info("SOLSCAN SAVING HOLDER INFO")
            (old_data, address) = self._deque.pop()
            print(f"checking the token address: {address}")
            self.fetch_url(address + r"#holders")
            try:
                retunred_holders = self.handle_csv_download(address)
                logging.info(f"Fetched data for {address} the data {retunred_holders}")
                yield self.pair_data(old_data=old_data, raw_data=retunred_holders)

            except StaleElementReferenceException:
                print("Stale element encountered, re-locating...")

                continue
            except NoSuchWindowException:
                print("Window already closed, breaking out of loop.")
                break

    def handle_csv_download(self, address) -> List:
        try:

            # Click CSV button
            csv_button = self._get_element(locator=self.main_locator, wait_time=5)
            if csv_button:
                csv_button.click()
                logging.info("CSV button clicked")

                # Wait for confirm button and click
                confirm_button = self._get_element(
                    locator=self.row_locator, wait_time=5
                )
                if confirm_button:
                    confirm_button.click()
                    logging.info("Confirm button clicked")

                    # Wait for and process download
                    download_file = self.wait_for_download(timeout=15)
                    print(f"downloaded file {download_file}")
                    if download_file:
                        df_holders = pd.read_csv(download_file)
                        logging.info(f"THE FILE IS: {df_holders}")
                        custom_path = Path(download_file)
                        new_name = f"{address}_data.csv"
                        self.rename_file_with_retry(custom_path, new_name)

                        print("file rename success")
                        logging.info(f"Downloaded file renamed to {custom_path}")
                        return [df_holders.to_dict(), address]

        except Exception as err:
            logging.error(f"Error: {err}")
            print(f"Error: {err}")
            # Ensure we're back on main window in case of error

    def wait_for_download(self, timeout=30, check_interval=1):
        """
        Waits for a file to be downloaded in the specified directory.
        """
        download_path = Path(self.download_path)
        end_time = time.time() + timeout

        while time.time() < end_time:
            files = list(download_path.glob("*.csv"))  # Check only for CSV files
            if files:
                newest_file = max(files, key=os.path.getctime)  # Most recently created

                # Check if the file is still being modified (crude check)
                initial_size = os.path.getsize(newest_file)
                time.sleep(check_interval)
                final_size = os.path.getsize(newest_file)

                if initial_size == final_size and initial_size > 0:
                    logging.info(f"Download complete: {newest_file}")
                    return str(newest_file)
                else:
                    logging.info(f"File {newest_file} is still downloading...")
            else:
                logging.info("No files found in download directory, waiting...")

            time.sleep(check_interval)

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
