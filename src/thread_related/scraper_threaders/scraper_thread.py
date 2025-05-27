from src.thread_related.scraper_threaders.services.Iservice import Iservice

from src.thread_related.scraper_threaders.services.Iservice import Iservice
from src.thread_related.scraper_threaders.services.scrape_service import scrape_service
from src.thread_related.scraper_threaders.base_threader import base_threader
from src.scrapers.Base_scraper import Base_scraper
from src.core.logger import ScraperLogger as log
from src.data.models import Address_Data as ad
from src.utils.TextProcessor import TextProcessor as tp
from src.DataFrameManager import DataFrameManager as dfm
from queue import Queue
from typing import Any
from threading import Thread
from src.thread_related.scraper_threaders.services.resources import (
    thread_resources as tr,
    queue_resources as qr,
)
from src.thread_related.distributor import dsitributor

class scraper_thread(base_threader):

    def __init__(
        self,
        name,
        logger,
        thread_r: tr,
        queue_r: qr,
        text_processor: Iservice,
        saver: Iservice,
        wait_event: Iservice,
        scraper: Iservice,
        topic: str,
        distributor: dsitributor,
        input_queue: Queue = None,
        output_queue: Queue = None,
    ):

        super().__init__(name, logger, thread_r, queue_r, input_queue, output_queue)


        if self.input_queue:
            distributor.subscribe(topic=topic, queue=input_queue, queue_name=self.name)
        self.distributor = distributor
        self.text_processor = text_processor
        self.saver = saver
        self.wait_event = wait_event
        self.scraper = scraper

    

        self.register_method("_wait", self._wait)
        self.register_method("_scrape", self._scrape)
        self.register_method("_process", self._process)
        self.register_method("_save", self._save)

    def name(self) -> str:
        return self.name

    def _wait(self):
        if self.wait_event:
            self.wait_event.run(self.input_queue)

    def _scrape(self):
        if self.scraper:
            self.scraper.run(self.input_queue)

    def _process(self):
        if self.text_processor:
            self.text_processor.run()

    def _save(self):
        if self.saver:
            if self.text_processor:
                self.saver.run(self.output_queue, local_queue=self.queue_r.processed_queue)
            else:
                self.saver.run(self.output_queue, local_queue=self.queue_r.data_buffer)

    # imroove this method later by centraling the cleanup process
    # and removing the need for this method in the child classes
    def _cleanup(self):
        if self.scraper:
            self.scraper.cleanup()  