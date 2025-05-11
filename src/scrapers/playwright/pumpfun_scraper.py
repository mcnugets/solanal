from src.scrapers.playwright.Base_scraper_p import Base_scraper_p
from typing import Annotated, Tuple, Optional
from src.core.logger import ScraperLogger as logger
import logging
import time
from colorama import Fore, Style
from playwright.sync_api import Error, Page, Locator # Add this import
# Define LocatorType as an alias for By



# def scrape_addresses(self):
#     # table = self.driver.find_element(By.XPATH, self.main_locator)

#     # /html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div/div[3]
#     # /html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div

#     # Scroll and scrape
#     # last_height = driver.execute_script("return arguments[0].scrollHeight", table)
#     try:
#         # Scroll down

#         time.sleep(2)  # Adjust the sleep time as needed

#         # Scrape the table content

#         # cell = rows[0].find_elements(By.CLASS_NAME, "g-table-cell")
#         rows = self.table.find_elements(self.row_locator)
#         # link = href.get_attribute("href")
#         for row in rows:

#             href = row.find_elements(By.TAG_NAME, "a")
#             print(row.text)
#             link = href[0].get_attribute("href")
#             address = link.split("/")[-1]

#             text = row.text + "#" + address
#             yield text
#     except:
#         print("Stale element reference: retrying...")

#         # Check if the scroll height has changed
#         # new_height = driver.execute_script("return arguments[0].scrollHeight", table)
#         # if new_height == last_height:
#         #     break
#         # last_height = new_height


class pumpfun_scraper(Base_scraper_p):

    def __init__(
        self,
        url: str,
        logger: logger,
        extra_locator: str| None = None,
        main_locator: str| None = None,
        row_locator: str| None = None,
        popup_locator: str| None = None,
        div_locator: Optional[Tuple] = None,
    ):
        super().__init__(

            main_locator=main_locator,
            row_locator=row_locator,
            popup_locator=popup_locator,
            url=url,
            logger=logger,
            extra_locator=extra_locator,
        )
        self.table = None
        self.div_locator = div_locator
        self.seen = set()
        self.is_website_ready = False

    def setup_website(self):
        try:
            self.fetch_url()
            self.handle_popup()
            # if self.extra_locator:
            #     self.handle_extra()
            self.table = self._page.locator(self.main_locator)
            logging.info("Website setup completed successfully.")
            self.is_website_ready = True
        except Exception as e:
            logging.error(f"An error occurred during website setup: {e}", exc_info=True)
            self.cleanup()
            self.is_website_ready = False
            raise  # Re-raise the exception to handle it at a higher level

    # (By.TAG_NAME, "tr")
    def _scrape_data(self):
        try:
            if not self.is_website_ready:
                self.setup_website()
            if self.table is None:
                error_msg = "Table locator not found - website may not have loaded properly"
                self._logger.log_warning(message="Table locator not found ")
                self._logger.log_info("Attempting to re-setup website...")
                self.setup_website()
                if self.table is None:  # Check again after retry
                    self._logger.log_critical(error_msg="Table still not found after retry, aborting scrape")
                    raise RuntimeError("Critical: Failed to locate table element after retry")
            divs = self.table.locator(self.row_locator)
            rows = divs.all()
            print(len(divs.all()))
            print("works")
        
            for row in rows:
                
                try:
                    first_cell: Locator = None
                    link_element = None
                    if self.div_locator:
                        
                        elements = row.locator(self.div_locator).all()
                        first_cell = elements[1]
                        link_element = elements[0].locator("a")
                    else:
                        first_cell = row
                        link_element = first_cell.locator('a').all()

                    # if not first_cell:
                    #     continue
                    print(first_cell.inner_text())
                    fltered_data = self.filter_noise(first_cell.inner_text())
                    print(fltered_data)
                    if fltered_data == None:
                        continue
                    
                
                    if link_element:
                        href = link_element[0].get_attribute("href")
                        address = href.split("/")[-1]
                        fltered_data += "#" + address
                    if address in self.seen:
                        print(f"already seen: {address} Skipping..")
                        continue
                    self.seen.add(address)

               
                    print("THE YIELDING SECTION")
        
                    yield self.validate_unprocessed(data=fltered_data, address=address)
                except TimeoutError:
                    print("Element became stale or not found, re-locating...")
                    continue
                except Error as e:
                    if "Target closed" in str(e):
                        print("Browser window closed, breaking out of loop.")
                        break
            # time.sleep(5)

        except Exception as e:
            print(f"There was an error in data scraping {e}")
            msg = f"An error occurred during data scraping: "
            
            self._logger.log_error(error_msg=msg, exc_info=e)

        finally:
            pass
    def filter_noise(self, raw_data: str) -> str | None:
        
        try:
            if not raw_data or not isinstance(raw_data, str):
                self._logger.log_warning("Invalid raw_data input in filter_noise")
                return None
                
            # Normalize line breaks and remove empty segments
            segments = [line.strip() for line in raw_data.split('\n') if line.strip()]

            # Check if the cleaned list length is within range
            if 11 <= len(segments) <= 50:
                return '#'.join(segments)

            return None
            
        except Exception as e:
            self._logger.log_error(
                error_msg="Error in filter_noise processing",
                exc_info=e
            )
            return None