"""Definition for the Ethereum DHT network.

The network stores records in a smart contract and can optionally leverage
Ethereum's Discovery v5 protocol for peer management.  Users must supply their
own list of bootstrap nodes when using discovery.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("eth", backend="ethereum"))
