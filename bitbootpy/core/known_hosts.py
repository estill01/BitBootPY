from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Union
from enum import Enum


class DHTNetwork(str, Enum):
    """Enumeration of supported DHT networks."""

    BIT_TORRENT = "bit_torrent"
    BTC = "btc"
    SOL = "sol"
    ETH = "eth"
    IPFS = "ipfs"
    ARWEAVE = "arweave"

    @classmethod
    def _missing_(cls, value: str) -> "DHTNetwork":
        """Dynamically create new enum members for unknown networks.

        This allows callers to register new networks at runtime simply by
        instantiating ``DHTNetwork`` with a string name.  The new member is
        added to the enum's internal mappings so subsequent lookups will return
        the same object.
        """

        # Normalize to lowercase just like the predefined values
        value = value.lower()
        new_member = str.__new__(cls, value)
        new_member._name_ = value.upper()
        new_member._value_ = value
        cls._value2member_map_[value] = new_member
        cls._member_map_[new_member._name_] = new_member
        return new_member


class DHTBackend(str, Enum):
    """Enumeration of available DHT backends."""

    KADEMLIA = "kademlia"


@dataclass(frozen=True)
class KnownHost:
    """Representation of a host and port combination."""

    host: str
    port: int

    def as_tuple(self) -> Tuple[str, int]:
        """Return the host/port pair as a ``(host, port)`` tuple."""

        return self.host, self.port


@dataclass(frozen=True)
class DHTConfig:
    """Configuration describing which DHT network/backend to use and where to listen."""

    network: DHTNetwork = DHTNetwork.BIT_TORRENT
    backend: DHTBackend = DHTBackend.KADEMLIA
    listen: KnownHost = KnownHost("0.0.0.0", 5678)


# Known bootstrap hosts for various networks. Only the BitTorrent network has
# real seed nodes at the moment but the structure allows additional networks or
# backends to be added in the future.
KNOWN_HOSTS: Dict[DHTNetwork, List[KnownHost]] = {
    DHTNetwork.BIT_TORRENT: [
        KnownHost("dht.transmissionbt.com", 6881),
        KnownHost("dht.u-phoria.org", 6881),
        KnownHost("dht.bt.am", 2710),
        KnownHost("dht.ipred.org", 6969),
        KnownHost("dht.pirateparty.gr", 80),
        KnownHost("dht.zoink.nl", 80),
        KnownHost("dht.openbittorrent.com", 80),
        KnownHost("dht.istole.it", 6969),
        KnownHost("dht.ccc.de", 80),
        KnownHost("dht.leechers-paradise.org", 6969),
    ],
    # Placeholder entries for additional networks/backends.
    DHTNetwork.BTC: [],
    DHTNetwork.SOL: [],
    DHTNetwork.ETH: [],
    DHTNetwork.IPFS: [],
    DHTNetwork.ARWEAVE: [],
}


def add_network(name: str, hosts: Optional[List[KnownHost]] = None) -> DHTNetwork:
    """Register a new network in :data:`KNOWN_HOSTS`.

    Args:
        name: Name of the network to register.
        hosts: Optional list of bootstrap hosts to associate with the network.

    Returns:
        The :class:`DHTNetwork` enum representing the newly added network.
    """

    network = DHTNetwork(name)
    KNOWN_HOSTS.setdefault(network, hosts or [])
    return network


def remove_network(name: Union[str, DHTNetwork]) -> None:
    """Remove a network and all associated hosts from :data:`KNOWN_HOSTS`."""

    network = DHTNetwork(name)
    KNOWN_HOSTS.pop(network, None)


def add_known_host(network: Union[str, DHTNetwork], host: KnownHost) -> None:
    """Add a bootstrap host to a network in :data:`KNOWN_HOSTS`."""

    net = DHTNetwork(network)
    KNOWN_HOSTS.setdefault(net, []).append(host)


def remove_known_host(network: Union[str, DHTNetwork], host: KnownHost) -> None:
    """Remove a bootstrap host from a network in :data:`KNOWN_HOSTS`."""

    net = DHTNetwork(network)
    hosts = KNOWN_HOSTS.get(net, [])
    try:
        hosts.remove(host)
    except ValueError:
        pass
