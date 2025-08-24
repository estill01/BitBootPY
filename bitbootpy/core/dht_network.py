"""DHT network definitions and registry.

This module replaces the previous ``known_hosts``/``DHTNetwork`` enum approach
with a fully dynamic registry.  Networks can be added or removed at runtime and
each network carries its bootstrap hosts and backend information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


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
        self._networks[network.name] = network
        return network

    def remove(self, name: str) -> None:
        self._networks.pop(name, None)

    def get(self, name: str) -> Optional[DHTNetwork]:
        return self._networks.get(name)

    def list(self) -> List[DHTNetwork]:
        return list(self._networks.values())

    # ------------------------------------------------------------------
    # Convenience helpers for manipulating bootstrap hosts
    # ------------------------------------------------------------------
    def add_known_host(self, name: str, host: KnownHost) -> DHTNetwork:
        network = self._networks.setdefault(name, DHTNetwork(name))
        network.bootstrap_hosts.append(host)
        return network

    def remove_known_host(self, name: str, host: KnownHost) -> None:
        network = self._networks.get(name)
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


def add_network(name: str, hosts: Optional[List[KnownHost]] = None) -> DHTNetwork:
    network = DHTNetwork(name, bootstrap_hosts=hosts or [])
    return DHT_NETWORK_REGISTRY.add(network)


def remove_network(name: str) -> None:
    DHT_NETWORK_REGISTRY.remove(name)


def add_known_host(network: str, host: KnownHost) -> None:
    DHT_NETWORK_REGISTRY.add_known_host(network, host)


def remove_known_host(network: str, host: KnownHost) -> None:
    DHT_NETWORK_REGISTRY.remove_known_host(network, host)


@dataclass(frozen=True)
class DHTConfig:
    """Configuration for running a local DHT node."""

    network: DHTNetwork = field(
        default_factory=lambda: DHT_NETWORK_REGISTRY.get("bit_torrent")
    )
    listen: KnownHost = KnownHost("0.0.0.0", 5678)

