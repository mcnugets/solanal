from .Iservice import Iservice
from .resources import thread_resources, queue_resources
from queue import Queue
from src.core.logger import ScraperLogger as log
from src.utils.TextProcessor import TextProcessor as tp
from src.scrapers.playwright.Base_scraper_p import Base_scraper_p
from abc import ABC, abstractmethod


class base_service(Iservice):

    def __init__(
        self,
        logger: log,
        thread_r: thread_resources,
        queue_r: queue_resources,
        scraper: Base_scraper_p | None = None,
        is_input_queue: bool | None = False,
    ):

        self.logger = logger
        self.thread_r = thread_r
        self.queue_r = queue_r
        self.scraper = scraper
        self.is_input_queue = is_input_queue

    @abstractmethod
    def run(self, input_queue: Queue | None = None):
        pass

    
