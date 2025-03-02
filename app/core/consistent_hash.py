import hashlib
from typing import List, Dict, Any
from bisect import bisect

class ConsistentHash:
    def __init__(self, nodes: List[str], virtual_nodes: int = 100):
        """
        Initialize the consistent hash ring
        
        Args:
            nodes: List of node identifiers (parsed from comma-separated string)
            virtual_nodes: Number of virtual nodes per physical node
        """
        self.virtual_nodes = virtual_nodes
        self.hash_ring = {}
        self.sorted_keys = []
        
        for node in nodes:
            self.add_node(node)

    def add_node(self, node: str) -> None:
        """
        Add a new node to the hash ring
        
        Args:
            node: Node identifier to add
        """
        for i in range(self.virtual_nodes):
            virtual_node_id = f"{node}#{i}"
            hash_key = self._hash(virtual_node_id)
            self.hash_ring[hash_key] = node
            self.sorted_keys.append(hash_key)
        self.sorted_keys.sort()

    def remove_node(self, node: str) -> None:
        """
        Remove a node from the hash ring
        
        Args:
            node: Node identifier to remove
        """
        for i in range(self.virtual_nodes):
            virtual_node_id = f"{node}#{i}"
            hash_key = self._hash(virtual_node_id)
            if hash_key in self.hash_ring:
                del self.hash_ring[hash_key]
                self.sorted_keys.remove(hash_key)

    def get_node(self, key: str) -> str:
        """
        Get the node responsible for the given key
        
        Args:
            key: The key to look up
            
        Returns:
            The node responsible for the key
        """
        if not self.sorted_keys:
            raise ValueError("Hash ring is empty")
            
        hash_key = self._hash(key)
        idx = bisect(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0  # Wrap around to the first node
        return self.hash_ring[self.sorted_keys[idx]]

    def _hash(self, key: str) -> int:
        """
        Generate a hash for the given key
        
        Args:
            key: The key to hash
            
        Returns:
            The hash of the key
        """
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
