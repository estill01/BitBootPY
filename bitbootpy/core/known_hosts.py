from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class KnownHost:
    """Representation of a known bootstrap host."""
    host: str
    port: int


# Known bootstrap hosts for various networks. Only the BitTorrent network has
# real seed nodes at the moment but the structure allows additional networks or
# backends to be added in the future.
KNOWN_HOSTS: Dict[str, List[KnownHost]] = {
    "bit_torrent": [
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
    "btc": [],
    "sol": [],
    "eth": [],
    "ipfs": [],
    "arweave": [],
}
