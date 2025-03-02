from typing import Dict, List, Any
import asyncio
from datetime import datetime
from ..core.redis_manager import RedisManager
from ..core.mem_cache_manager import MemCacheManager
from ..core.config import settings
from contextlib import asynccontextmanager

class VisitCounterService:
    def __init__(self):
        """Initialize the visit counter service with Redis manager"""
        self.redis_manager = RedisManager()
        self.mem_cache = MemCacheManager()
        self.running = True
        self.background_task = None

    async def batchFlusher(self):
        """Background task that periodically flushes buffered counts to Redis"""
        while self.running:
            try:
                await asyncio.sleep(30)  # sleep for 30 seconds
                print("Periodic buffer flush triggered")
                await self.mem_cache.flush(self.redis_manager)
            except Exception as e:
                print(f"Error in background flusher: {e}")
                # Continue running even if there's an error

    def _cache_valid(self, countData: Dict[str, Any]) -> bool:
        """
        Check if cache is valid for visit count
        
        Args:
            countData: Data from cache
            
        Returns:
            True if cache is valid, False otherwise
        """

        count_time = countData["ttl"]
        if (datetime.now() - count_time).seconds > settings.CACHE_TTL_SECONDS:
            return False
        return True
    
    async def flush_buffer(self) -> None:
        """
        Flush the buffer into Redis immediately
        This is used when we need to ensure Redis has the most up-to-date data
        """
        await self.mem_cache.flush(self.redis_manager)

    async def increment_visit(self, page_id: str) -> None:
        """
        Increment visit count for a page
        
        Args:
            page_id: Unique identifier for the page
        """
        # Add the visit to the in-memory buffer
        # The buffer will be periodically flushed to Redis by the background task,
        # or immediately flushed on cache miss during read operations
        self.mem_cache.buffer(page_id)


    async def get_visit_count(self, page_id: str) -> int:
        """
        Get current visit count for a page
        
        Args:
            page_id: Unique identifier for the page
            
        Returns:
            Current visit count
        """
        # Get cached count data
        count_data, served_via = self.mem_cache.get(page_id)
        cached_count = count_data["count"]
        
        # Get any pending counts from the buffer
        buffered_count = self.mem_cache.get_buffer_count(page_id)
        
        # If cache is invalid, get fresh data from Redis
        if not self._cache_valid(count_data):
            print("Cache invalid, getting latest count from Redis")
            # Flush buffer first to ensure Redis has the latest data
            await self.flush_buffer()
            # Get updated count from Redis
            redis_count, served_via = await self.redis_manager.get(page_id)
            # Update memory cache with the fresh count
            self.mem_cache.set_counts(page_id, redis_count)
            # Return Redis count plus any new buffer counts that accumulated during flush
            buffered_count = self.mem_cache.get_buffer_count(page_id)
            return redis_count + buffered_count, served_via
        else:
            # Return cached count plus buffered count
            return cached_count + buffered_count, served_via
        
        

