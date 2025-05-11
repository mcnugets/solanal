from src.scrapers.playwright.Base_scraper_p import Base_scraper_p
from typing import Annotated, Tuple
from selenium.webdriver.common.by import By as LocatorType
from collections import deque
from queue import Queue
import os
from src.core.logger import ScraperLogger as log
import time
import pandas as pd
from selenium.webdriver.common.by import By
from playwright.sync_api import Page
from src.data.models import Address_Data as ad


class gmgn_scraper(Base_scraper_p):

    def __init__(
        self,
        url,
        csv_path,
        logger: log,
        main_locator: str| None = None,
        row_locator: str| None = None,
        popup_locator: str| None = None,
       
    ):
        super().__init__(
            main_locator=main_locator,
            row_locator=row_locator,
            popup_locator=popup_locator,
            url=url,
            logger=logger
        )
        self.csv_path = csv_path
        self.has_data = False

    def _scrape_data(self):


        try:

            while len(self._deque) > 0:

                self._logger.log_info("GMGN ACTIVATED")
                address_data: ad = self._deque.pop()
                self.fetch_url(address_data.address)
                self.handle_popup()

                try:
                
                    row = self._page.locator(self.row_locator)
                    full_row = row.inner_text() + "#" + address_data.address
                    address_data.data = full_row
                    yield address_data

            
                except Exception as e:
                    print(f"Error fetching {address_data.address}: {e}")
                    self._logger.log_error(error_msg=f"Error fetching {address_data.address}", exc_info=e)
                    # continue

        finally:
            pass


    # TODO: if i want to expand on the data scraping im might have to separate
    # scraping function above(scrape_data) nto different components
    def scrape_top():
        pass

    def scrape_right():
        pass
