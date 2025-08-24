"""High-level network abstraction built on top of DHT networks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .dht_network import DHTNetwork, DHT_NETWORK_REGISTRY
from .network_names import NetworkName


@dataclass
class Network:
    """A logical network namespace backed by one or more DHT networks."""

    name: str
    dht_networks: List[DHTNetwork] = field(default_factory=list)

    def add_dht_network(self, network: DHTNetwork) -> None:
        if network not in self.dht_networks:
            self.dht_networks.append(network)


class NetworkRegistry:
    """Registry for :class:`Network` objects."""

    def __init__(self) -> None:
        self._networks: Dict[str, Network] = {}

    def add(self, network: Network) -> Network:
        self._networks[network.name] = network
        return network

    def get(self, name: str) -> Optional[Network]:
        return self._networks.get(name)

    def remove(self, name: str) -> None:
        self._networks.pop(name, None)

    def list(self) -> List[Network]:
        return list(self._networks.values())

    def create(
        self, name: str, dht_networks: Optional[List[DHTNetwork]] = None
    ) -> Network:
        dht_networks = dht_networks or [DHT_NETWORK_REGISTRY.get(NetworkName.BIT_TORRENT)]
        network = Network(name, dht_networks)
        return self.add(network)


# Global registry for higher-level networks
NETWORK_REGISTRY = NetworkRegistry()

