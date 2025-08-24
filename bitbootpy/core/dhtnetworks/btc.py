"""Definition for the Bitcoin DHT network.

The accompanying ``btc`` backend downloads Bitcoin Core's seed list to obtain
peers.  No static bootstrap hosts are bundled in the repository.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("btc", backend="btc"))
