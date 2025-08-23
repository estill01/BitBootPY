from __future__ import annotations
from typing import List, Optional

from kademlia.network import Server
from kademlia.routing import KBucket
import asyncio

from .known_hosts import KNOWN_HOSTS, KnownHost


class DHTManager:
    """Manage interaction with a DHT backend.

    Only the Kademlia backend is implemented at the moment but the class is
    structured so that alternative backends can be introduced later.  The
    manager bootstraps itself using known nodes for the selected network unless
    explicit bootstrap nodes are supplied.
    """

    def __init__(
        self,
        bootstrap_nodes: Optional[List[KnownHost]] = None,
        network: str = "bit_torrent",
        backend: str = "kademlia",
        listen_port: int = 5678,

    ):
        if backend != "kademlia":
            # Future backends can be selected here
            raise ValueError(f"Unsupported DHT backend: {backend}")

        self._server = Server()
        self._network = network
        self._bootstrap_nodes: List[KnownHost] = bootstrap_nodes or KNOWN_HOSTS.get(
            network, []
        )
        self._backend = backend
        self._listen_port = listen_port


    @classmethod
    async def create(
        cls,
        bootstrap_nodes: Optional[List[KnownHost]] = None,
        network: str = "bit_torrent",
        backend: str = "kademlia",
        listen_port: int = 5678,
    ) -> "DHTManager":
        """Asynchronously create and bootstrap a :class:`DHTManager`."""

        instance = cls(
            bootstrap_nodes,
            network=network,
            backend=backend,
            listen_port=listen_port,
        )
        await instance._bootstrap_dht()
        return instance

    async def _bootstrap_dht(self) -> None:
        """Start the local DHT node and bootstrap with known peers."""

        await self._server.listen(self._listen_port)

        # Connect to known nodes
        if self._bootstrap_nodes:
            await self._server.bootstrap(
                [(node.host, node.port) for node in self._bootstrap_nodes]
            )

    def get_routing_table(self) -> List[KBucket]:
        return self._server.protocol.router.buckets

    def is_server_started(self) -> bool:
        return bool(self._server.transport)

    async def wait_for_server_start(self):
        while not self._server.transport:
            await asyncio.sleep(0.1)

    def stop(self):
        self._server.stop()

    def get_server(self):
        return self._server

    def get_listening_host(self) -> KnownHost:
        """Return the address this node is listening on as a ``KnownHost``."""
        if not self._server.transport:
            raise RuntimeError("DHT server not started")
        host, port = self._server.transport.get_extra_info("sockname")
        return KnownHost(host, port)
