from collections import defaultdict
from datetime import datetime
from .redis_manager import RedisManager

class MemCacheManager:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemCacheManager, cls).__new__(cls)
            cls._instance.cache = defaultdict(dict)
            cls._instance.write_buffer = defaultdict(int)
        return cls._instance
    
    def buffer(self, page_id: str, count: int = 1) -> None:
        self.write_buffer[page_id] += count
    
    def get_buffer_count(self, page_id: str) -> int:
        return self.write_buffer.get(page_id, 0)
    
    async def flush(self, sink: RedisManager):
        if sink is None:
            print("No sink provided, skipping flush")
            return
        print("Flushing buffer to sink", datetime.now().isoformat())
        
        # Create a copy of the buffer to avoid race conditions
        buffer_to_flush = dict(self.write_buffer)
        if not buffer_to_flush:
            return
            
        # Clear buffer early to allow new writes to accumulate while we're flushing
        self.write_buffer.clear()
        
        # Bulk update Redis
        for page_id, count in buffer_to_flush.items():
            # Update in-memory cache with the flushed counts
            self.increment(page_id, count)
            # Update Redis
            await sink.increment(page_id, count)
    
    def increment(self, page_id: str, count: int = 1) -> None:
        if page_id not in self.cache:
            self.reset(page_id)
        
        self.cache[page_id] = {
            "count": self.cache[page_id]["count"] + count,
            "ttl": datetime.now()
        }
    
    def reset(self, page_id: str) -> None:
        self.cache[page_id] = {
            "count": 0,
            "ttl": datetime.now()
        }
    
    def set_counts(self, page_id: str, counts: int) -> None:
        self.cache[page_id] = {
            "count": counts,
            "ttl": datetime.now()
        }

    def get(self, page_id: str) -> int:


        if page_id not in self.cache:
            self.reset(page_id)

        return self.cache[page_id], "in_memory"