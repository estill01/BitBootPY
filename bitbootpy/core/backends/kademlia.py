from __future__ import annotations

"""Kademlia backend implementation wrapping :mod:`kademlia` library."""

from typing import Any, Iterable, Tuple
from kademlia.network import Server

from .base import BaseDHTBackend


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
