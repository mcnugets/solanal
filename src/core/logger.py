import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys
from queue import Queue
from threading import Lock
from rich.logging import RichHandler
from rich.console import Console


class ScraperLogger:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ScraperLogger, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

        self.queue_logs = {}  # Track queue sizes
        self.setup_logger("default")
        self.name = None
        self._initialized = True

    @property
    def name(self):
        """Get the current logger name"""
        return self._name

    @name.setter
    def name(self, value):
        """Set the logger name and update the logger instance"""
        self._name = value

    def log_warning(self, message: str):
        """Log a warning level message"""
        self.logger.warning(f"{self.name} - {message}")

    def _setup_config():
        logging.basicConfig

    def setup_logger(self, name):
        """Configure the logger with file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if logger.handlers:
            return

        # File handler
        log_file = (
            self.logs_dir / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Create formatters and add it to the handlers
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
        )
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")

        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(RichHandler(rich_tracebacks=True))

        self.logger = logger

    def log_queue_status(self, queue_name: str, queue: Queue):
        """Track and log queue sizes"""
        size = queue.qsize()
        self.queue_logs[queue_name] = size
        self.logger.debug(f"{self.name} - Queue '{queue_name}' size: {size}")

    def log_info(self, message: str):
        """Log an info level message"""
        self.logger.info(f"{self.name} - {message}")

    def log_type_data(self, message: str, data_type: str, data):
        """Log data of a specific type"""
        self.logger.debug(f"{self.name} - {message} - {data_type}: {data}")

    def log_scraper_event(
        self, scraper_name: str, event: str, data: Optional[dict] = None
    ):
        """Log scraper-specific events"""
        message = f"{self.name} - Scraper '{scraper_name}' - {event}"
        if data:
            message += f": {data}"
        self.logger.info(message)

    def log_error(self, error_msg: str, exc_info: Optional[Exception] = None):
        """Log errors with optional exception info"""
        if exc_info:
            self.logger.error(f"{self.name} - {error_msg}", exc_info=exc_info)
        else:
            self.logger.error(f"{self.name} - {error_msg}")

    def log_compilation(self, address: str, sources: set):
        """Log compilation events"""
        self.logger.info(
            f"{self.name} - Compiling data for {address} from sources: {sources}"
        )

    def log_sync_event(self, message: str):
        """Log synchronization events"""
        self.logger.debug(f"{self.name} - Sync: {message}")

    def get_queue_stats(self) -> dict:
        """Get current queue statistics"""
        return self.queue_logs.copy()
