"""DHT network definitions and registry.

This module replaces the previous ``known_hosts``/``DHTNetwork`` enum approach
with a fully dynamic registry.  Networks can be added or removed at runtime and
each network carries its bootstrap hosts and backend information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Union

from .network_names import NetworkName


@dataclass(frozen=True)
class KnownHost:
    """Representation of a host and port combination."""

    host: str
    port: int

    def as_tuple(self) -> Tuple[str, int]:
        return self.host, self.port


@dataclass
class DHTNetwork:
    """Description of a DHT network and how to bootstrap it."""

    name: str
    backend: str = "kademlia"
    bootstrap_hosts: List[KnownHost] = field(default_factory=list)


class DHTNetworkRegistry:
    """Registry holding all known :class:`DHTNetwork` objects."""

    def __init__(self) -> None:
        self._networks: Dict[str, DHTNetwork] = {}

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------
    def add(self, network: DHTNetwork) -> DHTNetwork:
        self._networks[str(network.name)] = network
        return network

    def remove(self, name: Union[str, NetworkName]) -> None:
        key = name.value if isinstance(name, NetworkName) else name
        self._networks.pop(key, None)

    def get(self, name: Union[str, NetworkName]) -> Optional[DHTNetwork]:
        key = name.value if isinstance(name, NetworkName) else name
        return self._networks.get(key)

    def list(self) -> List[DHTNetwork]:
        return list(self._networks.values())

    # ------------------------------------------------------------------
    # Convenience helpers for manipulating bootstrap hosts
    # ------------------------------------------------------------------
    def add_known_host(self, name: Union[str, NetworkName], host: KnownHost) -> DHTNetwork:
        key = name.value if isinstance(name, NetworkName) else name
        network = self._networks.setdefault(key, DHTNetwork(key))
        network.bootstrap_hosts.append(host)
        return network

    def remove_known_host(self, name: Union[str, NetworkName], host: KnownHost) -> None:
        key = name.value if isinstance(name, NetworkName) else name
        network = self._networks.get(key)
        if not network:
            return
        try:
            network.bootstrap_hosts.remove(host)
        except ValueError:
            pass


# Global registry instance used throughout the project
DHT_NETWORK_REGISTRY = DHTNetworkRegistry()

# Import built-in backends so they can register their networks
from . import backends as _backends  # noqa: F401


# ---------------------------------------------------------------------------
# Helper functions mirroring the API of the old ``known_hosts`` module.  These
# are primarily used by tests and external code and act as a thin wrapper around
# :data:`DHT_NETWORK_REGISTRY`.
# ---------------------------------------------------------------------------


def add_network(name: Union[str, NetworkName], hosts: Optional[List[KnownHost]] = None) -> DHTNetwork:
    key = name.value if isinstance(name, NetworkName) else name
    network = DHTNetwork(key, bootstrap_hosts=hosts or [])
    return DHT_NETWORK_REGISTRY.add(network)


def remove_network(name: Union[str, NetworkName]) -> None:
    DHT_NETWORK_REGISTRY.remove(name)


def add_known_host(network: Union[str, NetworkName], host: KnownHost) -> None:
    DHT_NETWORK_REGISTRY.add_known_host(network, host)


def remove_known_host(network: Union[str, NetworkName], host: KnownHost) -> None:
    DHT_NETWORK_REGISTRY.remove_known_host(network, host)


@dataclass(frozen=True)
class DHTConfig:
    """Configuration for running a local DHT node."""

    network: DHTNetwork = field(
        default_factory=lambda: DHT_NETWORK_REGISTRY.get(NetworkName.BIT_TORRENT)
    )
    listen: KnownHost = KnownHost("0.0.0.0", 5678)

