"""A local in-memory DHT network used for tests.

No bootstrap hosts are defined and the default Kademlia backend is used.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("local"))
