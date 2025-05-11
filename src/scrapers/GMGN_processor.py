from .Base_scraper import Base_scraper
from typing import Annotated, Tuple
from selenium.webdriver.common.by import By as LocatorType
from collections import deque
from queue import Queue
import os
import logging
import time
import pandas as pd
from selenium.webdriver.common.by import By
from ..data.models import DequeChange
from src.data.models import Address_Data as ad


class gmgn_processor(Base_scraper):

    def __init__(
        self,
        driver_path,
        main_locator: Annotated[
            Tuple[LocatorType, str],
            {
                "description": "Tuple containing locator type and selector string for main element"
            },
        ],
        row_locator,
        popup_locator,
        url,
        csv_path,
    ):
        super().__init__(
            driver_path=driver_path,
            main_locator=main_locator,
            row_locator=row_locator,
            popup_locator=popup_locator,
            url=url,
        )
        self.csv_path = csv_path
        self.has_data = False

    def _scrape_data(self):

        # self.load_csv_to_deque()

        try:

            while len(self._deque) > 0:

                logging.info("GMGN works")
                print("GMGN works")
                address_data: ad = self._deque.pop()
                self.fetch_url(address_data.address)
                self.handle_popup()

                try:
                    time.sleep(5)

                    row = self._get_element(locator=self.row_locator)
                    row = row.text + "#" + address_data.address
                    address_data.data = row
                    yield address_data

                    # yield row

                    # print(f"Fetched data for {address}")

                except Exception as e:
                    print(f"Error fetching {address_data.address}: {e}")
                    logging.error(f"Error fetching {address_data.address}: {e}")
                    # continue

            # else:
            #     time.sleep(0.1)

        finally:
            pass

    def _on_deque_change(self, change: DequeChange) -> None:
        """Handle deque changes"""
        if change.operation == "append":
            self.has_data = True
            logging.info(f"New data available in deque: {change.new_value[-1]}")
        elif change.operation == "pop":
            self.has_data = len(change.new_value) > 0

    # TODO: if i want to expand on the data scraping im might have to separate
    # scraping function above(scrape_data) nto different components
    def scrape_top():
        pass

    def scrape_right():
        pass
