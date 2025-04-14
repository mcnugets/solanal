from typing import Dict
from src.thread_related.scraper_threaders.scraper_thread import scraper_thread
from src.scrapers.GMGN_processor import gmgn_processor
from src.scrapers.PumpFun_processor import pumpfun_processor
from src.scrapers.solscan_scraper import solscan_processor


# we gotta create another pydantic validator for all the dicionary shit
class threader_factory:
    @classmethod
    def create_threader(cls, threader_type: str, configs: Dict):

        if threader_type == "scraper":
            return scraper_thread()
        elif threader_type == "llm":
            pass

    def create_scraper(cls, scraper_type: str, configs: Dict):
        if scraper_type == "pumpfun" or scraper_type == "gmgn2":
            return pumpfun_processor(**configs["scraper_configs"])
        elif scraper_type == "gmgn":
            return gmgn_processor(**configs["scraper_configs"])

        elif scraper_type == "solscan":
            return solscan_processor(**configs["scraper_configs"])
