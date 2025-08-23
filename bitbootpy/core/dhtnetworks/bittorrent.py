"""Definition for the BitTorrent DHT network."""

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY, KnownHost

DHT_NETWORK_REGISTRY.add(
    DHTNetwork(
        "bit_torrent",
        bootstrap_hosts=[
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
    )
)
