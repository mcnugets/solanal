from src.Base_scraper import Base_scraper, CSVLoaderMixin
from typing import Annotated, Tuple
from selenium.webdriver.common.by import By as LocatorType
from collections import deque
from queue import Queue
import os
import logging
import time
import pandas as pd
from selenium.webdriver.common.by import By


class gmgn_processor(Base_scraper, CSVLoaderMixin):

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
        input_queue,
        inner_queue,
    ):
        super().__init__(
            driver_path=driver_path,
            main_locator=main_locator,
            row_locator=row_locator,
            popup_locator=popup_locator,
            url=url,
        )
        self.csv_path = csv_path
        self.input_queue = input_queue
        self.inner_queue = inner_queue
        self.deque = None

    def _scrape_data(self):

        self.load_csv_to_deque()

        try:
            while self.deque:
                address = self.deque.pop()
                self.fetch_url(address)
                self.handle_popup()

                try:
                    time.sleep(5)

                    row = self._get_element(locator=self.row_locator)
                    row = row.text + "#" + address
                    yield row

                    # print(f"Fetched data for {address}")

                except Exception as e:
                    print(f"Error fetching {address}: {e}")
                    # continue

        finally:
            pass

    # TODO: if i want to expand on the data scraping im might have to separate
    # scraping function above(scrape_data) nto different components
    def scrape_top():
        pass

    def scrape_right():
        pass
