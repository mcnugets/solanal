from .Base_scraper import Base_scraper
from typing import Annotated, Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchWindowException,
)
import logging
import time
from colorama import Fore, Style

# Define LocatorType as an alias for By
LocatorType = By


def scrape_addresses(self):
    # table = self.driver.find_element(By.XPATH, self.main_locator)

    # /html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div/div[3]
    # /html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div

    # Scroll and scrape
    # last_height = driver.execute_script("return arguments[0].scrollHeight", table)
    try:
        # Scroll down

        time.sleep(2)  # Adjust the sleep time as needed

        # Scrape the table content

        # cell = rows[0].find_elements(By.CLASS_NAME, "g-table-cell")
        rows = self.table.find_elements(self.row_locator)
        # link = href.get_attribute("href")
        for row in rows:

            href = row.find_elements(By.TAG_NAME, "a")
            print(row.text)
            link = href[0].get_attribute("href")
            address = link.split("/")[-1]

            text = row.text + "#" + address
            yield text
    except:
        print("Stale element reference: retrying...")

        # Check if the scroll height has changed
        # new_height = driver.execute_script("return arguments[0].scrollHeight", table)
        # if new_height == last_height:
        #     break
        # last_height = new_height


class pumpfun_processor(Base_scraper):

    def __init__(
        self,
        driver_path,
        main_locator: Annotated[
            Tuple[LocatorType, str],
            {
                "description": "Tuple containing locator type and selector string for main element"
            },
        ],
        row_locator: Annotated[
            Tuple[LocatorType, str],
            {
                "description": "Tuple containing locator type and selector string for main element"
            },
        ],
        popup_locator: Annotated[
            Tuple[LocatorType, str],
            {
                "description": "Tuple containing locator type and selector string for main element"
            },
        ],
        url,
        div_locator: Optional[Tuple] = None,
    ):
        super().__init__(
            driver_path=driver_path,
            main_locator=main_locator,
            row_locator=row_locator,
            popup_locator=popup_locator,
            url=url,
        )
        self.table = None
        self.div_locator = div_locator

    def setup_website(self):
        try:
            self.fetch_url()
            self.handle_popup()
            self.table = self.load_html_element()
            logging.info("Website setup completed successfully.")
        except Exception as e:
            logging.error(f"An error occurred during website setup: {e}")
            self.cleanup()

    # (By.TAG_NAME, "tr")
    def _scrape_data(self):
        try:
            if self.table is None:
                logging.error("Table not found, exiting...")
                print("Table not found, exiting...")
                return
            locator, element = self.row_locator
            rows = self.table.find_elements(locator, element)
            print("works")

            for row in rows:
                # /html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table/tbody/tr[1]/td[1]
                try:
                    temp_str = ""
                    first_cell = None
                    link_element = None
                    if self.div_locator:
                        elements = row.find_elements(self.div_locator)
                        first_cell = elements[1]
                        link_element = elements[0].find_elements(By.TAG_NAME, "a")
                    else:
                        first_cell = row
                        link_element = first_cell.find_elements(By.TAG_NAME, "a")

                    if not first_cell:
                        continue

                    temp_str = first_cell.text

                    if link_element:
                        href = link_element[0].get_attribute("href")
                        address = href.split("/")[-1]
                        temp_str += "#" + address

                    print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
                    print(
                        f"{Fore.LIGHTGREEN_EX}RAW TEXT RETRIEVED: {temp_str}{Style.RESET_ALL}"
                    )
                    print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")

                    yield self.pair_data(raw_data=temp_str)
                except StaleElementReferenceException:
                    print("Stale element encountered, re-locating...")

                    continue
                except NoSuchWindowException:
                    print("Window already closed, breaking out of loop.")
                    break
            time.sleep(5)

        except Exception as e:
            print(f"There was an error in data scraping {e}")
            logging.error(f"An error occurred during data scraping: {e}")

        finally:
            pass
