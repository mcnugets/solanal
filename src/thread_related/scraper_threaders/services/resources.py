from dataclasses import dataclass
from threading import Event, Lock, Condition
from queue import Queue
from src.DataFrameManager import DataFrameManager as dfm
from src.utils.TextProcessor import TextProcessor as tp


@dataclass
class thread_resources:
    stop_event: Event
    save_trigger: Event
    data_lock: Lock
    driver_lock: Lock
    process_lock: Lock
    condition: Condition


@dataclass
class queue_resources:
    data_buffer: Queue
    processed_queue: Queue
