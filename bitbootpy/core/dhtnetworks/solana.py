"""Definition for the Solana DHT network.

The ``solana`` backend contacts the public mainnet RPC endpoint and extracts
gossip peers.  Additional bootstrap hosts can be supplied if desired.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("solana", backend="solana"))
