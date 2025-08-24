"""Definition for the Arweave DHT network.

Currently this is only a stub; no bootstrap hosts are provided.  The
``arweave`` backend persists values on the Arweave permaweb.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("arweave", backend="arweave"))
