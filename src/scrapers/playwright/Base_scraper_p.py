from typing import Tuple, Literal, Annotated, Optional, List, Any, Union
from playwright.async_api import Browser, Playwright, BrowserContext, async_playwright, Page
from collections import deque
from src.data.models import Address_Data as ad
from abc import abstractmethod
from playwright_stealth import stealth_async
from src.core.logger import ScraperLogger as log

from contextlib import asynccontextmanager

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
    async def _scrape_data(self) -> ad | None:
        pass
    
    def validate_unprocessed(
        self, address: str | None = None, data: List | str | None = None
    ) -> ad:
        return ad(address=address, data=data)
    
    async def setup_browser(self, p: Playwright):
        browser = await p.chromium.launch(headless=False,
                                        args=[
                                            "--no-sandbox",
                                            "--disable-setuid-sandbox",
                                            "--disable-dev-shm-usage",
                                            "--disable-gpu",
                                            '--disable-popup-blocking',
                                            '--enable-javascript'
                                        ],
                                        downloads_path=self.download_path)
        return browser
    
    async def setup_context(self, browser: Browser):
         user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.114 Safari/537.36"
         context = await browser.new_context(
                 user_agent=user_agent,
                 ignore_https_errors=True,
                 accept_downloads=True
            )
         return context

    async def setup_page(self, context: BrowserContext):
        page = await context.new_page()
        return page

    async def run_p(self):
        try:
            if not self._page:
                self._pw = await async_playwright().start()
                self._browser = await self.setup_browser(self._pw)
                self._context = await self.setup_context(self._browser)
                self._page = await self.setup_page(self._context)
        except Exception as e:
            self._logger.log_error(f"Failed to initialize Playwright: {str(e)}", exc_info=e)
            if hasattr(self, '_page') and self._page:
                await self._page.close()
            if hasattr(self, '_context') and self._context:
                await self._context.close()
            if hasattr(self, '_browser') and self._browser:
                await self._browser.close()
            if hasattr(self, '_pw') and self._pw:
                await self._pw.stop()
            raise
      
    @asynccontextmanager
    async def session(self):
        try:
            await self.run_p()
            yield self
        except Exception as e:
            self._logger.log_error(f"Error during Playwright session: {str(e)}", exc_info=e)
            raise
        finally:
            await self.cleanup()

    async def start_scrape(self):
        try:
            async with self.session():
                try:
                    balls = await self._scrape_data()
                    yield from self._scrape_data()
                except Exception as e:
                    self._logger.log_error(f"Error during data scraping: {str(e)}", exc_info=e)
                    raise
        except Exception as e:
            self._logger.log_error(f"Error during scraping session: {str(e)}", exc_info=e)
            raise

    async def handle_popup(self):
        try:
            if not self.popup_locator:
                return
            if not self._page:
                self._logger.log_warning("Cannot handle popup - page not initialized")
                return
            
            try:
                popup = self._page.locator(self.popup_locator)
                if await popup.count() > 0:
                    await popup.click()
                    self._logger.log_info("Successfully handled popup")
                else:
                    self._logger.log_warning("Popup locator not found on page")
            except Exception as e:
                self._logger.log_error(f"Failed to handle popup: {str(e)}", exc_info=e)
                raise
                
        except Exception as e:
            self._logger.log_error(f"Unexpected error in handle_popup: {str(e)}", exc_info=e)
            raise

    async def fetch_url(self, url_query: str = "") -> None:
        url = f'{self.url}{url_query}'
        try:
            await self._page.goto(url=url)
        except Exception as e:
            raise RuntimeError(f"Failed to navigate to URL {url}: {e}") from e

    async def cleanup(self):
        if self._page is not None:
            await self._page.close()     
        if self._context is not None:
            await self._context.close()  
        if self._browser is not None:
            await self._browser.close()   
        if self._pw is not None:
            await self._pw.stop()
