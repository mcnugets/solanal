from typing import Dict, List
from src.thread_related.scraper_threaders.scraper_thread import scraper_thread
from src.scrapers.playwright.Base_scraper_p import Base_scraper_p
from src.thread_related.scraper_threaders.services.scrape_service import scrape_service
from src.thread_related.scraper_threaders.services.wait_service import wait_service
from src.thread_related.scraper_threaders.services.saving_service import saving_service
from src.thread_related.scraper_threaders.services.tp_service import (
    text_processor_service,
)
from src.thread_related.scraper_threaders.services.resources import (
    thread_resources,
    queue_resources,
)
from src.core.logger import ScraperLogger as log
from threading import Event, Condition, Lock
from queue import Queue
from dataclasses import dataclass
from src.DataFrameManager import DataFrameManager as dfm
from src.utils.TextProcessor import TextProcessor as tp
from src.thread_related.scraper_threaders.validators import (
    pumpfun_validator,
    gmgm_validator,
    holders_validator,
    gmgn_two_validator,
)
from src.scrapers.playwright.gmgn_scraper import gmgn_scraper
from src.scrapers.playwright.pumpfun_scraper import pumpfun_scraper
from src.scrapers.playwright.solscan_scraper import solscan_scraper
from src.thread_related.DataCompiler import DataCompiler, validate_sources
from src.core.config import queue_m
from src.thread_related.distributor import dsitributor

@dataclass
class context_resources:
    thread_r: thread_resources
    queue_r: queue_resources
    logger: log
logger = log()

# TODO: CREATE ORCHESTRAION FOR ALL THE THREADERS
# TODO: CREATE PYDANTIC VALIDATORS FOR ALL THESE DATA PASS3D
# TODO: we gotta top have cotext resources more integrated into a code
# we gotta create another pydantic validator for all the dicionary shit
class threader_factory:

    @classmethod
    def create_threader(
        cls,
        threader_type: str,
        configs: Dict,
        topic: str,
        distributor:dsitributor,
        scraper_type: str | None = None,
        input_queue: Queue | None = None,
        output_queue: Queue | None = None,
     
    ):
        
        topic = topic

        distributor.add_topic(topic=topic)
        if threader_type == "scrapers":
            #
            logger.name = scraper_type
            scraper_cfg = configs.get(threader_type)
            scrape_specific_cfg = scraper_cfg.get(scraper_type)
            service_wait = scrape_specific_cfg.get("wait")
            service_scraper = scrape_specific_cfg.get("scraper")
            service_saving = scrape_specific_cfg.get("save")
            service_tp = scrape_specific_cfg.get("process")
            #

            thread_r = thread_resources(
                stop_event=Event(),
                condition=Condition(),
                driver_lock=Lock(),
                save_trigger=Event(),
                process_lock=Lock(),
                data_lock=Lock(),
            )
            queue_r = queue_resources(data_buffer=Queue(), 
                                      processed_queue=Queue())
            res = context_resources(thread_r=thread_r, 
                                    queue_r=queue_r, 
                                    logger=logger)
            waiting_service = None
            scraper_service = None
            saving_service = None
            tp_service = None

            # scraper_dic = configs.get("scraper")
            if scraper_type in scraper_cfg:
                scraper = cls.create_scraper(logger=logger,
                    scraper_type=scraper_type, 
                    configs=scrape_specific_cfg["scraper_configs"]
                )
                if service_scraper:
                    scraper_service = cls.create_scraper_service(
                        res=res, scraper=scraper
                    )
                if service_wait:
                    waiting_service = cls.create_wait_service(res=res, 
                                                              scraper=scraper)
            if service_saving:
                saving_service = cls.create_saver_service(
                    logger=logger,
                    res=res,
                    scraper_type=scraper_type,
                    distributor=distributor,
                    topic=topic,
                    configs=scrape_specific_cfg,
                )

            if service_tp:
                tp_service = cls.create_text_processor_service(
                    res=res,
                    patterns=scrape_specific_cfg["patterns"],
                    cleaning_pat=configs["global"]["cleaning_patterns"],
                )
           
            return scraper_thread(
                name=scraper_type,
                logger=logger,
                thread_r=thread_r,
                queue_r=queue_r,
                wait_event=waiting_service,
                text_processor=tp_service,
                saver=saving_service,
                scraper=scraper_service,
                input_queue=input_queue,
                output_queue=output_queue,
                distributor=distributor,
                topic=topic,
            )
        elif threader_type == "llm":
            pass

    @classmethod
    def create_data_compiler(
        self,
        distributor: dsitributor,
        topic: str,
        configs: Dict
    ) -> DataCompiler:
        logger.log_info(f"Creating data compiler for {topic}")
        input_queues = {
            col: queue_m.get_queue(col)["output_queue"]
            for col in configs['data_sources']
        }
        distributor.add_topic(topic=topic)
        data_sources = validate_sources(
            gmgn_2=configs["data_sources"][0],
            holders=configs["data_sources"][1]
        )
        compiler = DataCompiler(
            input_queues=input_queues,
            output_queue=queue_m.get_queue("compiled")["output_queue"],
            logger=logger,
            data_sources=data_sources,
            dsitributor=distributor,
            topic=topic
        )
        return compiler

    @classmethod
    def create_scraper(
        cls,
        logger: log,
        scraper_type: str,
        configs: Dict
    ) -> Base_scraper_p:
        configs.pop("type", None)
        configs["logger"] = logger
        try:
            if scraper_type in ("pumpfun", "gmgn_2"):
                if not configs:
                    raise ValueError(
                        f"Missing scraper_configs for {scraper_type}"
                    )
                return pumpfun_scraper(**configs)
            elif scraper_type == "gmgn":
                if not configs:
                    raise ValueError(
                        f"Missing scraper_configs for {scraper_type}"
                    )
                return gmgn_scraper(**configs)
            elif scraper_type == "solscan":
                if not configs:
                    raise ValueError(
                        f"Missing scraper_configs for {scraper_type}"
                    )
                return solscan_scraper(**configs)
            else:
                raise ValueError(f"Unsupported scraper type: {scraper_type}")
        except KeyError as e:
            raise ValueError(f"Invalid configuration format: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to create scraper: {str(e)}")

    @classmethod
    def create_scraper_service(
        cls,
        res: context_resources,
        scraper: Base_scraper_p,
    ):
        return scrape_service(
            scraper=scraper,
            logger=res.logger,
            thread_r=res.thread_r,
            queue_r=res.queue_r,
            is_input_queue=False,
        )

    @classmethod
    def create_wait_service(
        cls,
        res: context_resources,
        scraper: Base_scraper_p
    ):
        return wait_service(
            logger=res.logger,
            thread_r=res.thread_r,
            queue_r=res.queue_r,
            scraper=scraper,
        )

    @classmethod
    def create_saver_service(
        cls,
        logger,
        scraper_type: str,
        res: context_resources,
        distributor: dsitributor,
        topic: str,
        configs: Dict
    ):
        vlaidator = None
        if scraper_type == "pumpfun":
            vlaidator = pumpfun_validator()
        elif scraper_type == "gmgn_2":
            vlaidator = gmgn_two_validator()
        elif scraper_type == "gmgn":
            vlaidator = gmgm_validator()
        elif scraper_type == "solscan":
            vlaidator = holders_validator()

        df_manager = dfm(
            logger=logger,
            scraper_type=scraper_type,
            columns=configs["columns"],
            base_file=configs["base_file"],
        )

        return saving_service(
            logger=res.logger,
            thread_r=res.thread_r,
            queue_r=res.queue_r,
            df_manager=df_manager,
            data_validatoer=vlaidator,
            distributor=distributor,
            topic=topic,
            columns=configs["columns"],
        )

    @classmethod
    def create_text_processor_service(
        cls,
        res: context_resources,
        patterns: Dict,
        cleaning_pat: Dict
    ):
        text_p = tp(
            logger=res.logger,
            patterns=patterns,
            CLEANING_PATTERNS=cleaning_pat,
        )
        return text_processor_service(
            logger=res.logger,
            thread_r=res.thread_r,
            queue_r=res.queue_r,
            text_processor=text_p,
        )
