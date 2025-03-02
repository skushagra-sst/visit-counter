import redis
from typing import Dict, List, Optional, Any
from .consistent_hash import ConsistentHash
from .config import settings

class RedisManager:
    def __init__(self):
        """Initialize Redis connection pools and consistent hashing"""
        self.connection_pools: Dict[str, redis.ConnectionPool] = {}
        self.redis_clients: Dict[str, redis.Redis] = {}
        
        # Parse Redis nodes from comma-separated string
        redis_nodes = [node.strip() for node in settings.REDIS_NODES.split(",") if node.strip()]
        self.consistent_hash = ConsistentHash(redis_nodes, settings.VIRTUAL_NODES)
        
        # Initialize connection pools for each Redis node
        for node in redis_nodes:
            try:
                pool = redis.ConnectionPool.from_url(node)
                self.connection_pools[node] = pool
                self.redis_clients[node] = redis.Redis(connection_pool=pool)
            except Exception as e:
                print(f"Failed to initialize Redis connection for {node}: {str(e)}")

    async def get_connection(self, key: str, get_name: bool = False) -> redis.Redis:
        """
        Get Redis connection for the given key using consistent hashing
        
        Args:
            key: The key to determine which Redis node to use
            
        Returns:
            Redis client for the appropriate node
        """
        # TODO: Implement getting the appropriate Redis connection
        # 1. Use consistent hashing to determine which node should handle this key
        # 2. Return the Redis client for that node
        # pass

        node = self.consistent_hash.get_node(key)
        if get_name:
            host = node.split("//")[1].split(":")[0]
            return self.redis_clients[node], host

        return self.redis_clients[node]

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in Redis
        
        Args:
            key: The key to increment
            amount: Amount to increment by
            
        Returns:
            New value of the counter
        """
        # TODO: Implement incrementing a counter
        # 1. Get the appropriate Redis connection
        # 2. Increment the counter
        # 3. Handle potential failures and retries
        # return 0
        conn = await self.get_connection(key)
        conn.incrby(key, amount)

    async def get(self, key: str) -> Optional[int]:
        """
        Get value for a key from Redis
        
        Args:
            key: The key to get
            
        Returns:
            Value of the key or None if not found
        """
        # TODO: Implement getting a value
        # 1. Get the appropriate Redis connection
        # 2. Retrieve the value
        # 3. Handle potential failures and retries
        # return None

        conn, conn_name = await self.get_connection(key, get_name=True)
        res = conn.get(key)
        if res:
            return int(res), conn_name
        return 0, conn_name
