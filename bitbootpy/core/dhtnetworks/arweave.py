"""Definition for the Arweave DHT network.

The ``arweave`` backend queries the public ``/peers`` endpoint to discover
nodes.  Users may supply their own bootstrap hosts or backend if more advanced
functionality is required.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("arweave", backend="arweave"))
