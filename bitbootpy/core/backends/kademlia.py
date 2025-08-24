from __future__ import annotations

"""Kademlia backend implementation wrapping :mod:`kademlia` library."""

from typing import Any, Iterable, Tuple
from kademlia.network import Server

from ..dht_network import KnownHost
from .base import BaseDHTBackend
from . import register_backend_with_network


class KademliaBackend(BaseDHTBackend):
    """Thin wrapper around :class:`kademlia.network.Server`."""

    def __init__(self) -> None:
        self.server = Server()

    async def listen(self, port: int) -> None:
        await self.server.listen(port)

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:
        if nodes:
            await self.server.bootstrap(list(nodes))

    async def get(self, key: bytes) -> Any:
        return await self.server.get(key)

    async def set(self, key: bytes, value: Any) -> bool:
        return await self.server.set(key, value)

    def stop(self) -> None:
        self.server.stop()

    def get_listening_host(self) -> Tuple[str, int]:
        if not self.server.transport:
            raise RuntimeError("Kademlia server not started")
        host, port = self.server.transport.get_extra_info("sockname")
        return host, port


# Register networks using the unified registry
register_backend_with_network(
    "kademlia",
    KademliaBackend,
    network_name="bit_torrent",
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

register_backend_with_network("kademlia", KademliaBackend, network_name="local")
