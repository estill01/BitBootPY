"""Definition for the Ethereum DHT network.

This network relies on the ``eth`` backend which downloads the list of
bootnodes published by the `go-ethereum` project.  Users can provide their own
node list by overriding the backend or supplying explicit bootstrap hosts.
"""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY

DHT_NETWORK_REGISTRY.add(DHTNetwork("eth", backend="eth"))
