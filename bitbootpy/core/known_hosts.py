from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum


class DHTNetwork(str, Enum):
    """Enumeration of supported DHT networks."""

    BIT_TORRENT = "bit_torrent"
    BTC = "btc"
    SOL = "sol"
    ETH = "eth"
    IPFS = "ipfs"
    ARWEAVE = "arweave"


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
