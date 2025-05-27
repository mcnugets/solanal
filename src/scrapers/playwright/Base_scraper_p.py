from typing import Tuple, Literal, Annotated, Optional, List, Any, Union
from playwright.sync_api import Browser, Playwright, BrowserContext, sync_playwright, Page
from collections import deque
from src.data.models import Address_Data as ad
from abc import abstractmethod
from playwright_stealth import stealth_sync
from src.core.logger import ScraperLogger as log
from fake_useragent import UserAgent
from contextlib import contextmanager
from pathlib import Path
class Base_scraper_p:
    def __init__(
        self,
        url: str,
        logger: log,
        main_locator: str | None = None,
        popup_locator: str | None = None,
        row_locator: str | None = None,
        download_path: str | None = None,
        extra_locator: str | None = None
    ):
        
        self.main_locator = f'xpath={main_locator}'
        self.popup_locator = f'xpath={popup_locator}'
        self.row_locator = f'xpath={row_locator}'
        self.url = url
        self.extra_locator =  f'xpath={extra_locator}'
        self.download_path = download_path
        
        self._deque = deque(maxlen=100)
        self._page = None
        self._context = None
        self._browser = None
        self._pw = None
        self._logger = logger


    @abstractmethod
    def _scrape_data(self) -> ad | None:
        pass
    
    # TODO: future note to myself: create pydantic model for the data
    def validate_unprocessed(
        self, address: str | None = None, data: List | str | None = None
    ) -> ad:
        return ad(address=address, data=data)
    
    def setup_browser(self, p: Playwright):
    
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--window-size=1920,1080",
            "--start-maximized",  
            "--disable-popup-blocking",
            "--incognito",
            "--disable-setuid-sandbox",
            "--enable-javascript"
        ]
        browser = p.chromium.launch(headless=False,
                                        args=launch_args,
                                        downloads_path=self.download_path)
        return browser
    
    def setup_context(self, browser: Browser):
        # user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.114 Safari/537.36"
        ua = UserAgent()
        user_agent = ua.random
        context = browser.new_context(
                user_agent=user_agent,
                ignore_https_errors=True,
                storage_state="auth.json" if Path("auth.json").exists() else None,
                extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                accept_downloads=True # Enable downloads
                #  record_download_dir=self.download_dir, # Set download location
                 # Add other context options here (permissions, storage state, etc.)
            )
        return context
    def save_session(self):
        if self._context:
            self._context.storage_state(path="auth.json")  # Save cookies
    def setup_page(self, context: BrowserContext):
        page = context.new_page()
        # stealth_sync()
        return page
    # TODO: saving this as a potential further development
    # def goto(self, page: Page):
    #     page.goto(self.url)
    def run_p(self):
        try:
            if not self._page:
                p = sync_playwright()
                self._pw = p.start()
                self._browser = self.setup_browser(self._pw)
                self._context = self.setup_context(browser=self._browser)
         
                self._page = self.setup_page(context=self._context)
        except Exception as e:
            self._logger.log_error(f"Failed to initialize Playwright: {str(e)}", exc_info=e)
            # Clean up any partially initialized resources
            if hasattr(self, '_page') and self._page:
                self._page.close()
            if hasattr(self, '_context') and self._context:
                self._context.close()
            if hasattr(self, '_browser') and self._browser:
                self._browser.close()
            if hasattr(self, '_pw') and self._pw:
                self._pw.stop()
            raise  # Re-raise to allow higher level handling
      
    @contextmanager
    def session(self):
    
        try:
            self.run_p()  # Initialize Playwright and browser
            yield  # Yield the instance for use in with block
        except Exception as e:
            self._logger.log_error(f"Error during Playwright session: {str(e)}", exc_info=e)
            raise
        # finally:
            # # self.cleanup()  # Ensure resources are always cleaned up
            # self.save_session()
    def start_scrape(self):
        try:
            with self.session():
                try:
               
                    yield from  self._scrape_data()
                except Exception as e:
                    self._logger .log_error(f"Error during data scraping: {str(e)}", exc_info=e)
                    raise
        except Exception as e:
            self._logger.log_error(f"Error during scraping session: {str(e)}", exc_info=e)
            raise



    # def load_html_element(self):
    #     pass
    # def _get_element(self):
    #     pass
    def handle_popup(self):
        try:
            if not self.popup_locator:
                return
            if not self._page:
                self._logger.log_warning("Cannot handle popup - page not initialized")
                return
            
            try:
                popup = self._page.locator(self.popup_locator)
                if popup.count() > 0:
                    popup.click()
                    self._logger.log_info("Successfully handled popup")
                else:
                    self._logger.log_warning("Popup locator not found on page")
            except Exception as e:
                self._logger.log_error(f"Failed to handle popup: {str(e)}", exc_info=e)
                raise
                
        except Exception as e:
            self._logger.log_error(f"Unexpected error in handle_popup: {str(e)}", exc_info=e)
            raise

   
    def fetch_url(self, url_query: str = "") -> None:
        
        url = f'{self.url}{url_query}'
        self._logger.log_info(f'the url itself mothafucka: {url}')
        try:
            self._page.goto(url=url)  # 10 second timeout
            self._page.wait_for_load_state()  # Wait for all network activity to settle
        except Exception as e:
            raise RuntimeError(f"Failed to navigate to URL {url}: {e}") from e

    def cleanup(self):
      
        if self._page is not None:
            self._page.close()     
        if self._context is not None:
            self._context.close()  
        if self._browser is not None:
            self._browser.close()   
        if  self._pw is not None:
             self._pw.stop()
