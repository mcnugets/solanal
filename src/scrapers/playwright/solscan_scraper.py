from .Base_scraper_p import Base_scraper_p
from typing import Annotated, Tuple, List
from collections import deque
import os
import logging
import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from pathlib import Path
from src.core.logger import ScraperLogger as logger
from playwright.sync_api import Error  # Add this import

from src.data.models import Address_Data as ad

# import aiohttp


class solscan_scraper(Base_scraper_p):

    def __init__(
        self,
        main_locator: str,
        popup_locator: str, 
        row_locator: str,
        url: str,
        csv_path: str,
        download_path: str,
    ):
        self.csv_path = csv_path

        super().__init__(
            logger=logger,
            main_locator=main_locator,
            popup_locator=popup_locator,
            row_locator=row_locator,
            url=url,
            download_path=download_path,
        )


    def _scrape_data(self):
        # self.load_csv_to_deque()

        while len(self._deque) > 0:

            self._logger.log_info(message="SOLSCAN SAVING HOLDER INFO")
            address_data: ad = self._deque.pop()
            print(f"checking the token address: {address_data.address}")
            self.fetch_url(address_data.address + r"#holders")
            try:
                retunred_holders = self.handle_csv_download(address_data.address)
                self._logger.log_info(
                    message=f"Fetched data for {address_data.address} the data {retunred_holders}"
                )
                address_data.data = retunred_holders
                yield address_data

            except TimeoutError:
                print("Element became stale or not found, re-locating...")
                continue
            except Error as e:
                if "Target closed" in str(e):
                    print("Browser window closed, breaking out of loop.")
                    break

    def handle_csv_download(self, address) -> List:
        try:

            # Click CSV button
            csv_button = self._page.locator(self.main_locator)
            if csv_button:
                csv_button.click()
                self._logger.log_info(message="CSV button clicked")
                # Wait for confirm button and click
               
                confirm_button = self._page.locator(self.row_locator)
                if confirm_button:
                    confirm_button.click()
                    self._logger.log_info(message="Confirm button clicked")

                    # Wait for and process download
                    download_file = self.wait_for_download(timeout=15)
                    print(f"downloaded file {download_file}")
                    if download_file:
                        df_holders = pd.read_csv(download_file)
                        self._logger.log_info(message=f"THE FILE IS: {df_holders}")
                        custom_path = Path(download_file)
                        new_name = f"{address}_data.csv"
                        self.rename_file_with_retry(custom_path, new_name)

                        self._logger.log_info(message="file rename success")
                        self._logger.log_info(message=f"Downloaded file renamed to {custom_path}")
                        return [df_holders.to_dict(), address]

        except Exception as err:
            self._logger.log_error(error_msg=f"Error occurred during CSV download for address {address}: {str(err)}", exc_info=err)
            self._logger.log_error(error_msg=f"[ERROR] Failed to process CSV download for {address}. Error details: {str(err)}")
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
                    self._logger.log_info(message=f"Download complete: {newest_file}")
                    return str(newest_file)
                else:
                    self._logger.log_info(message=f"File {newest_file} is still downloading...")
            else:
                self._logger.log_info(message="No files found in download directory, waiting...")

            time.sleep(check_interval)

        self._logger.log_error(error_msg="Download timed out")
        return None

    def handle_popup(self):
        pass

    def rename_file_with_retry(self, src: Path, dst: str, retries: int = 5, delay: float = 1.0) -> None:
        """Attempt to rename a file with retries on Windows permission errors.
        
        Args:
            src: Path object of source file
            dst: New filename (without path)
            retries: Number of retry attempts
            delay: Seconds to wait between retries
            
        Raises:
            PermissionError: If all retries fail and file is still locked
            OSError: For other file operation errors
        """
        new_path = src.with_name(dst)
        
        for attempt in range(1, retries + 1):
            try:
                src.replace(new_path)  # Use replace() instead of rename() for cross-platform atomicity
                self._logger.log_info(f"Successfully renamed file to {new_path}")
                return
            except PermissionError as e:
                # Handle both Windows (winerror=32) and Linux (errno=13 or 16) file lock errors
                if (hasattr(e, 'winerror') and e.winerror == 32) or \
                   (hasattr(e, 'errno') and e.errno in (13, 16)):  # File lock errors
                    self._logger.log_warning(
                        f"File {src} is locked (attempt {attempt}/{retries}), retrying in {delay} sec..."
                    )
                    time.sleep(delay)
                else:
                    raise
            except OSError as e:
                self._logger.log_error(f"File operation failed: {str(e)}")
                raise

        raise PermissionError(
            f"Failed to rename {src} after {retries} attempts. File may still be locked."
        )


if __name__ == "__main__":
    URL = "https://solscan.io/token/"
    main_locator = (
        By.XPATH,
        "/html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/button",
    )
    row_locator = (By.XPATH, "/html/body/div[3]/div[3]/button[2]")
    ss = solscan_scraper(
        main_locator=main_locator,
        popup_locator=(),
        row_locator=row_locator,
        url=URL,
        csv_path="../pumpfun_data.csv",
        download_path="../holders",
        driver_path=r"C:\Users\sulta\AppData\Local\Programs\Python\Python310\lib\site-packages\chromedriver_autoinstaller\131\chromedriver.exe",
    )
    ss._scrape_data()
