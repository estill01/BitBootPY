"""Definition for the Ethereum DHT network.

No bootstrap hosts are provided and the network requires the optional
``eth-discv5`` backend.  Users must supply their own list of Discovery v5
nodes for bootstrapping.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("eth", backend="eth-discv5"))
