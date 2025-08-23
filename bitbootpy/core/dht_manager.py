from __future__ import annotations

from typing import Dict, List, Optional, Union

from kademlia.network import Server
from kademlia.routing import KBucket
import asyncio

from .dht_network import (
    KnownHost,
    DHTConfig,
    DHTBackend,
    DHTNetwork,
    DHT_NETWORK_REGISTRY,
)


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
        config: Optional[DHTConfig] = None,
    ):
        self._config = config or DHTConfig()

        if self._config.network.backend != DHTBackend.KADEMLIA:
            # Future backends can be selected here
            raise ValueError(
                f"Unsupported DHT backend: {self._config.network.backend}"
            )

        self._server = Server()
        self._bootstrap_nodes: List[KnownHost] = (
            bootstrap_nodes or self._config.network.bootstrap_hosts
        )


    @classmethod
    async def create(
        cls,
        bootstrap_nodes: Optional[List[KnownHost]] = None,
        config: Optional[DHTConfig] = None,
    ) -> "DHTManager":
        """Asynchronously create and bootstrap a :class:`DHTManager`."""

        instance = cls(bootstrap_nodes, config=config)
        await instance._bootstrap_dht()
        return instance

    async def _bootstrap_dht(self) -> None:
        """Start the local DHT node and bootstrap with known peers."""

        await self._server.listen(self._config.listen.port)

        # Connect to known nodes
        if self._bootstrap_nodes:
            await self._server.bootstrap(
                [node.as_tuple() for node in self._bootstrap_nodes]
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

    async def switch_network(
        self,
        network: Union[str, DHTNetwork],
        bootstrap_nodes: Optional[List[KnownHost]] = None,
    ) -> None:
        """Switch the underlying DHT network and re-bootstrap the server."""

        self.stop()
        if isinstance(network, str):
            net = DHT_NETWORK_REGISTRY.get(network)
            if net is None:
                raise ValueError(f"Unknown DHT network: {network}")
        else:
            net = network

        self._config = DHTConfig(network=net, listen=self._config.listen)
        self._server = Server()
        self._bootstrap_nodes = bootstrap_nodes or net.bootstrap_hosts
        await self._bootstrap_dht()


class MultiDHTManager:
    """Manage multiple :class:`DHTManager` instances, one per DHT network."""

    def __init__(self) -> None:
        self._managers: Dict[str, DHTManager] = {}

    def add_network(
        self, network: Union[str, DHTNetwork], bootstrap_nodes: Optional[List[KnownHost]] = None
    ) -> DHTManager:
        if isinstance(network, str):
            net = DHT_NETWORK_REGISTRY.get(network)
            if net is None:
                raise ValueError(f"Unknown DHT network: {network}")
        else:
            net = network

        manager = DHTManager(
            bootstrap_nodes=bootstrap_nodes, config=DHTConfig(network=net)
        )
        self._managers[net.name] = manager
        return manager

    async def add_network_async(
        self, network: Union[str, DHTNetwork], bootstrap_nodes: Optional[List[KnownHost]] = None
    ) -> DHTManager:
        if isinstance(network, str):
            net = DHT_NETWORK_REGISTRY.get(network)
            if net is None:
                raise ValueError(f"Unknown DHT network: {network}")
        else:
            net = network

        manager = await DHTManager.create(
            bootstrap_nodes=bootstrap_nodes, config=DHTConfig(network=net)
        )
        self._managers[net.name] = manager
        return manager

    def get_manager(self, name: str) -> Optional[DHTManager]:
        return self._managers.get(name)

    def remove_network(self, name: str) -> None:
        manager = self._managers.pop(name, None)
        if manager:
            manager.stop()

    def list_networks(self) -> List[DHTNetwork]:
        return [m._config.network for m in self._managers.values()]
