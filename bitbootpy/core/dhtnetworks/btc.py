"""Definition for the Bitcoin DHT network.

No bootstrap hosts are bundled.  This entry primarily acts as a placeholder so
that projects can supply their own bootstrap list at runtime.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("btc", backend="bitcoin"))
