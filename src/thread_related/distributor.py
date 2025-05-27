from queue import Queue
from typing import Dict, List
from src.thread_related.scraper_threaders.Ithreader import Idata_validator
from src.core.logger import ScraperLogger as log
class dsitributor:
    def __init__(self,  logger: log) -> None:
        self.topics: Dict[str, List[Queue]] = {}
        self.logger = logger
    def add_topic(self, topic: str) -> None:
    
        try:
            if not topic or not isinstance(topic, str):
                raise ValueError("Topic name must be a non-empty string")
                
            if topic in self.topics:
                self.logger.log_warning(f"Topic '{topic}' already exists")
                return
                
            self.topics[topic] = []
            self.logger.log_info(f"Added new topic: {topic}")
            
        except Exception as e:
            self.logger.log_error(f"Error adding topic '{topic}': {str(e)}")
            raise
    
    def publish(self, topic: str, data: Dict) -> None:
        try:
            if not topic:
                error_msg = "Empty topic name provided for publishing"
                self.logger.log_error(error_msg)
                raise ValueError(error_msg)
                
            if topic not in self.topics:
                error_msg = f"Attempted to publish to non-existent topic: {topic}. Available topics: {list(self.topics.keys())}"
                self.logger.log_error(error_msg)
                raise KeyError(error_msg)
                
            self.logger.log_info(f"Starting publish to topic '{topic}' with data type: {type(data)}")
            self.logger.log_info(f"Data being published: {str(data)[:200]}...")  # Truncate long data
            
            queue_count = len(self.topics[topic])
            self.logger.log_info(f"Publishing to {queue_count} queue(s) for topic '{topic}'")

            for i, queue in enumerate(self.topics[topic]):
                try:
                    queue_size_before = queue.qsize()
                    queue.put(data)
                    queue_size_after = queue.qsize()
                    
                    self.logger.log_info(
                        f"Published data to queue {i+1}/{queue_count} for topic '{topic}'. "
                        f"Queue size changed from {queue_size_before} to {queue_size_after}"
                    )
                except Exception as e:
                    self.logger.log_error(
                        f"Failed to publish to queue {i+1}/{queue_count} in topic '{topic}'. "
                        f"Queue type: {type(queue)}, Error: {str(e)}",
                        exc_info=True
                    )
                    continue
                    
        except Exception as e:
            self.logger.log_error(f"Unexpected error in publish for topic '{topic}': {str(e)}")
            raise

    def subscribe(self, topic: str, queue: Queue, queue_name: str) -> None:
     
        try:
            if not topic or topic not in self.topics:
                error_msg = f"Attempted to subscribe to non-existent topic: {topic}"
                self.logger.log_error(error_msg)
                raise KeyError(error_msg)
                
        
            self.topics[topic].append(queue)
            self.logger.log_info(f"Added queue subscription for topic: {topic} with queue name: {queue_name}. Current topic size: {len(self.topics[topic])}")
        except Exception as e:
            self.logger.log_error(f"Error subscribing to topic '{topic}' with queue name '{queue_name}': {str(e)}")
            raise
