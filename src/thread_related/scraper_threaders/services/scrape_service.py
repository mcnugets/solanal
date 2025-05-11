from src.thread_related.scraper_threaders.services.base_service import base_service
from queue import Queue
from src.data.models import Address_Data as ad
import logging
import time
from src.thread_related.scraper_threaders.services.resources import (
    thread_resources,
    queue_resources,
)
from src.scrapers.playwright.Base_scraper_p import Base_scraper_p
from src.core.logger import ScraperLogger as log


class scrape_service(base_service):

    def __init__(
        self,
        logger: log,
        thread_r: thread_resources,
        queue_r: queue_resources,
        scraper: Base_scraper_p,
        is_input_queue: bool,
    ) -> None:
        super().__init__(logger, thread_r, queue_r, scraper, is_input_queue)

    def run(self, input_queue: Queue):
        try:
            if input_queue:
                with self.thread_r.condition:
                    while (
                        self.scraper._deque.__len__() <= 0
                        and not self.thread_r.stop_event.is_set()
                    ):
                        self.thread_r.condition.wait()

            if self.thread_r.stop_event.is_set():
                return
            # with self.thread_r.driver_lock:  # Protect driver initialization
            #     self.scraper.setup_website()

            while not self.thread_r.stop_event.is_set():
                print("TESTING THE WHILR LOOP ")
                try:
                    if input_queue and not self.is_input_queue:
                        #  we found the loop hole
                        self.logger.log_info("Starting scraping...")
                        with self.thread_r.condition:
                            self.thread_r.condition.wait(
                                timeout=2
                            )  # Prevent tight loop if input queue is empty
                            # continue

                    scrape_gen = self.scraper.start_scrape()
                    temp_pair_data: ad = next(
                        scrape_gen
                    )  # Get the next piece of data
                    self.logger.log_info(f"scraped raw data {temp_pair_data}")
                    with self.thread_r.condition:
                        while self.queue_r.data_buffer.full():
                            self.thread_r.condition.wait()

                        self.queue_r.data_buffer.put(temp_pair_data)

                        self.thread_r.condition.notify_all()
                        # Add data and notify

                except StopIteration:
                    self.logger.log_info("Scraping completed - no more data to scrape")
                    break  # Exit the loop when scraping is complete

                except Exception as e:
                    self.logger.log_error(
                        error_msg=f"Critical scraping error occurred: {str(e)}", 
                        exc_info=e
                    )
                    if isinstance(e, (RuntimeError, KeyboardInterrupt)):
                        raise  # Re-raise critical exceptions
                    continue  # Continue scraping for non-critical errors
        except Exception as e:
            self.logger.log_error(f"Error during scraping: {str(e)}", exc_info=e)
        finally:
            self.cleanup()

    
    def cleanup(self):
        """Clean up resources used by the scraper"""
        try:
            self.scraper.cleanup()
            
            # if hasattr(self.scraper, "driver") and self.scraper.driver:
            #     self.scraper.driver.quit()
        except Exception as e:
            self.logger.log_error(f"Error during cleanup: {str(e)}", exc_info=e)
