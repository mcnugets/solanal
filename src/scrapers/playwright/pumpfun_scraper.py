from src.scrapers.playwright.Base_scraper_p import Base_scraper_p
from typing import Annotated, Tuple, Optional
from src.core.logger import ScraperLogger as logger
import logging
import time
from colorama import Fore, Style
from playwright.sync_api import Error, Page, Locator # Add this import
# Define LocatorType as an alias for By
import re


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
        self.is_popuphandled = False

    def setup_website(self):
        try:
            self.fetch_url()
            if  self.is_popuphandled:
                self.is_popuphandled = True
                self.handle_popup()
            # if self.extra_locator:
            #     self.handle_extra()
           
            logging.info("Website setup completed successfully.")
            self.is_website_ready = True
        except Exception as e:
            logging.error(f"An error occurred during website setup: {e}", exc_info=True)
            self.cleanup()
            self.is_website_ready = False
            raise  # Re-raise the exception to handle it at a higher level

    # (By.TAG_NAME, "tr")
    def _scrape_data(self):
        while True:
            try:
                if not self.is_website_ready:
                    self.setup_website()
                self._page.wait_for_selector(self.main_locator)
                self.table = self._page.locator(self.main_locator)
                if self.table is None:  # Check again after retry
                    self._logger.log_warning(error_msg="Table still not found, retrying....")
                    continue
                self.table.wait_for(state='visible', timeout=5000)
                divs = self.table.locator(self.row_locator)
                rows = divs.all()
                print(len(divs.all()))
                print("works")
            
                for i, row in enumerate(rows):
                    print(f' index {i}   length {len(rows)-1}')
                    try:
                        first_cell: Locator = None
                        link_element: Locator = None
                  
                  
                        # if not first_cell:
                        #     continue
                        row.wait_for(state='visible', timeout=2000)
                        fltered_data = self.filter_noise(
                            row.inner_text(timeout=5000))
                        if not fltered_data:
                            print('the variable is NULL wil vause issues')
                            continue
                        else:
                            print(fltered_data)
                            if self.div_locator:
                            
                                elements = row.locator(self.div_locator).all()
                                first_cell = elements[1]
                                link_element = elements[0].locator("a")
                            else:
                                first_cell = row
                                link_element = first_cell.locator('a').all()
                            # this bulshit needs to be in the tp_service
                            if link_element: 
                                address = self.extract_solana_address_from_url(
                                    link_element[-1].get_attribute('href')
                                )
                    
                                fltered_data += "#" + address
                        # bulshit ends here
                        if address in self.seen:
                            print(f"already seen: {address} Skipping..")
                            # time.sleep(3)
                            continue
                        self.seen.add(address)

                        
                        print("THE YIELDING SECTION")
            
                        yield self.validate_unprocessed(data=fltered_data, address=address)
                    
                    except TimeoutError:
                        print("Element became stale or not found, re-locating...")
                        time.sleep(5)
                        continue
                    except Error as e:
                        if "Target closed" in str(e):
                            print("Browser window closed, breaking out of loop.")
                #             break
                time.sleep(5)

            except Exception as e:
                print(f"There was an error in data scraping {e}")
                msg = f"An error occurred during data scraping: "
                
                self._logger.log_error(error_msg=msg, exc_info=e)

        # finally:
        #     pass
    def filter_noise(self, raw_data: str) -> str | None:
        
        try:
            if not raw_data or not isinstance(raw_data, str):
                self._logger.log_warning("Invalid raw_data input in filter_noise")
                return None
                
            # Normalize line breaks and remove empty segments
            segments = [line.strip() for line in raw_data.split('\n') if line.strip()]

            # Check if the cleaned list length is within range
            if 11 <= len(segments) <= 50:
                return '\n'.join(segments)

            return None
            
        except Exception as e:
            self._logger.log_error(
                error_msg="Error in filter_noise processing",
                exc_info=e
            )
            return None
        
    # temporarily here but would have to be moved to tp_service
    def extract_solana_address_from_url(self, url_string: str) -> Optional[str]:
        try:
            self._logger.log_warning(f'address url input: {url_string}')
            if not isinstance(url_string, str) or not url_string.strip():
                self._logger.log_warning("Invalid URL string provided to extract_solana_address_from_url")
                return None

            try:
                pattern_twitter = re.compile(r'q=\(\$?[^\s)]+\s+OR\s+([1-9A-HJ-NP-Za-km-z]{32,44})\)|q=\(([1-9A-HJ-NP-Za-km-z]{32,44})\s+OR\s+\$?[^\s)]+\)')
                pattern_solscan = re.compile(r'/sol/token/([1-9A-HJ-NP-Za-km-z]{32,44})(?:[/?]|\Z)')
            except re.error as e:
                self._logger.log_error(f"Regex compilation error: {str(e)}", exc_info=e)
                return None

            try:
                # Try the Twitter pattern first
                match_twitter = pattern_twitter.search(url_string)
                if match_twitter:
                    address = match_twitter.group(1) if match_twitter.group(1) else match_twitter.group(2)
                    if address and len(address) in range(32, 45):  # Validate length
                        return address
            except Exception as e:
                self._logger.log_error(f"Error processing Twitter pattern: {str(e)}", exc_info=e)

            try:
                # Try the Solscan pattern
                match_solscan = pattern_solscan.search(url_string)
                if match_solscan:
                    address = match_solscan.group(1)
                    if address and len(address) in range(32, 45):  # Validate length
                        return address
            except Exception as e:
                self._logger.log_error(f"Error processing Solscan pattern: {str(e)}", exc_info=e)
            self._logger.log_warning(f'Noen of the methods worked hence we retrbn just url: {url_string}')
            return url_string

        except Exception as e:
            self._logger.log_error(f"Unexpected error in extract_solana_address_from_url: {str(e)}", exc_info=e)
            return None
