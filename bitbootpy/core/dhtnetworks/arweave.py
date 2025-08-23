"""Definition for the Arweave DHT network.

Currently this is only a stub; no bootstrap hosts or custom backend are
provided.  Users interested in Arweave integration should register bootstrap
nodes and an appropriate backend themselves.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("arweave"))
