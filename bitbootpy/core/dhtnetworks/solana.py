"""Definition for the Solana DHT network.

This module registers the ``solana`` network which expects a backend named
``solana``.  The provided backend is a placeholder and users need to supply
bootstrap hosts separately.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("solana", backend="solana"))
