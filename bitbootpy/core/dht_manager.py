from __future__ import annotations

from typing import Dict, List, Optional, Union

from kademlia.routing import KBucket
import asyncio

from .dht_network import (
    KnownHost,
    DHTConfig,
    DHTNetwork,
    DHT_NETWORK_REGISTRY,
)
from .network_names import NetworkName
from .backends import (
    BACKEND_REGISTRY,
    BaseDHTBackend,
    set_backend_for_network as _set_backend_for_network_mapping,
)


class DHTManager:
    """Manage interaction with a DHT backend.

    The manager delegates all DHT operations to a pluggable backend selected via
    the :class:`~bitbootpy.core.dht_network.DHTNetwork` configuration.  Backends
    are looked up in :data:`bitbootpy.core.backends.BACKEND_REGISTRY` and can be
    extended by third-party packages.
    """

    def __init__(
        self,
        bootstrap_nodes: Optional[List[KnownHost]] = None,
        config: Optional[DHTConfig] = None,
    ):
        self._config = config or DHTConfig()

        backend_factory = BACKEND_REGISTRY.get(self._config.network.backend)
        if backend_factory is None:
            raise ValueError(
                f"Unsupported DHT backend: {self._config.network.backend}"
            )
        self._backend: BaseDHTBackend = backend_factory()
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

        await self._backend.listen(self._config.listen.port)

        # Connect to known nodes
        if self._bootstrap_nodes:
            await self._backend.bootstrap(
                [node.as_tuple() for node in self._bootstrap_nodes]
            )

    def get_routing_table(self) -> List[KBucket]:
        server = getattr(self._backend, "server", None)
        if server and getattr(server, "protocol", None):
            return server.protocol.router.buckets
        return []

    def is_server_started(self) -> bool:
        server = getattr(self._backend, "server", None)
        return bool(getattr(server, "transport", None))

    async def wait_for_server_start(self):
        while not self.is_server_started():
            await asyncio.sleep(0.1)

    def stop(self):
        self._backend.stop()

    # ------------------------------------------------------------------
    # Convenience wrappers around backend operations
    # ------------------------------------------------------------------
    async def get(self, key: bytes):
        return await self._backend.get(key)

    async def set(self, key: bytes, value):
        return await self._backend.set(key, value)

    def get_server(self):
        """Return the backend instance for direct access if needed."""
        return self._backend

    def get_listening_host(self) -> KnownHost:
        host, port = self._backend.get_listening_host()
        return KnownHost(host, port)

    async def switch_network(
        self,
        network: Union[str, NetworkName, DHTNetwork],
        bootstrap_nodes: Optional[List[KnownHost]] = None,
    ) -> None:
        """Switch the underlying DHT network and re-bootstrap the server."""

        self.stop()
        if isinstance(network, (str, NetworkName)):
            net = DHT_NETWORK_REGISTRY.get(str(network))
            if net is None:
                raise ValueError(f"Unknown DHT network: {network}")
        else:
            net = network

        self._config = DHTConfig(network=net, listen=self._config.listen)
        backend_factory = BACKEND_REGISTRY.get(net.backend)
        if backend_factory is None:
            raise ValueError(f"Unsupported DHT backend: {net.backend}")
        self._backend = backend_factory()
        self._bootstrap_nodes = bootstrap_nodes or net.bootstrap_hosts
        await self._bootstrap_dht()


class MultiDHTManager:
    """Manage multiple :class:`DHTManager` instances, one per DHT network."""

    def __init__(self) -> None:
        self._managers: Dict[str, DHTManager] = {}

    def add_network(
        self, network: Union[str, NetworkName, DHTNetwork], bootstrap_nodes: Optional[List[KnownHost]] = None
    ) -> DHTManager:
        if isinstance(network, (str, NetworkName)):
            net = DHT_NETWORK_REGISTRY.get(str(network))
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
        self, network: Union[str, NetworkName, DHTNetwork], bootstrap_nodes: Optional[List[KnownHost]] = None
    ) -> DHTManager:
        if isinstance(network, (str, NetworkName)):
            net = DHT_NETWORK_REGISTRY.get(str(network))
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

    async def set_backend_for_network(
        self,
        network: Union[str, NetworkName],
        backend_key: str,
        bootstrap_nodes: Optional[List[KnownHost]] = None,
    ) -> DHTManager:
        """Repoint a DHT network to a different backend and apply it.

        - Updates the global registry mapping for the network name.
        - If a manager for this network exists, switches it asynchronously.
        - Otherwise, creates and bootstraps a new manager for the network.
        """
        # Update registry mapping
        _set_backend_for_network_mapping(network, backend_key)

        # Resolve concrete network config
        net_key = network.value if isinstance(network, NetworkName) else str(network)
        net = DHT_NETWORK_REGISTRY.get(net_key)
        if net is None:
            raise ValueError(f"Unknown DHT network after mapping: {net_key}")

        existing = self._managers.get(net.name)
        if existing is not None:
            await existing.switch_network(net, bootstrap_nodes)
            return existing

        # Create a new manager if one didn't exist
        manager = await DHTManager.create(
            bootstrap_nodes=bootstrap_nodes or net.bootstrap_hosts,
            config=DHTConfig(network=net),
        )
        self._managers[net.name] = manager
        return manager
