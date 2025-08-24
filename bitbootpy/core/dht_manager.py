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

        # Instantiate all configured backends for this network
        self._backends: Dict[str, BaseDHTBackend] = {}
        for cfg in self._config.network.backends:
            factory = BACKEND_REGISTRY.get(cfg.backend)
            if factory is None:
                raise ValueError(f"Unsupported DHT backend: {cfg.backend}")
            self._backends[cfg.backend] = factory()

        # Default bootstrap nodes is the union across backends unless provided
        self._bootstrap_nodes: List[KnownHost] = (
            bootstrap_nodes or self._config.network.all_bootstrap_hosts()
        )

    # Back-compat shim used by tests to override the single backend
    @property
    def _backend(self) -> BaseDHTBackend:
        # Return the first backend instance
        return next(iter(self._backends.values()))

    @_backend.setter
    def _backend(self, value: BaseDHTBackend) -> None:
        # Replace all with a single entry for testing
        self._backends = {"__test__": value}


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

        for backend in self._backends.values():
            await backend.listen(self._config.listen.port)
            # Connect to known nodes
            if self._bootstrap_nodes:
                await backend.bootstrap([node.as_tuple() for node in self._bootstrap_nodes])

    def get_routing_table(self) -> List[KBucket]:
        # Prefer a server that exposes a routing table (e.g., kademlia)
        for backend in self._backends.values():
            server = getattr(backend, "server", None)
            if server and getattr(server, "protocol", None):
                return server.protocol.router.buckets
        return []

    def is_server_started(self) -> bool:
        for backend in self._backends.values():
            server = getattr(backend, "server", None)
            if bool(getattr(server, "transport", None)):
                return True
        return False

    async def wait_for_server_start(self):
        while not self.is_server_started():
            await asyncio.sleep(0.1)

    def stop(self):
        for backend in self._backends.values():
            backend.stop()

    # ------------------------------------------------------------------
    # Convenience wrappers around backend operations
    # ------------------------------------------------------------------
    async def get(self, key: bytes):
        # Query all backends concurrently and merge results
        async def _one(b: BaseDHTBackend):
            try:
                return await b.get(key)
            except Exception:
                return None

        results = await asyncio.gather(*[_one(b) for b in self._backends.values()])

        # Merge policy: if any list/tuple/set returned, combine unique entries
        merged_seq = []
        have_seq = False
        for r in results:
            if isinstance(r, (list, tuple, set)):
                have_seq = True
                for item in r:
                    if item not in merged_seq:
                        merged_seq.append(item)
        if have_seq:
            return merged_seq
        # Otherwise return first non-None scalar
        for r in results:
            if r is not None:
                return r
        return None

    async def set(self, key: bytes, value):
        # Broadcast set to all backends; consider success if any succeed
        async def _one(b: BaseDHTBackend):
            try:
                return await b.set(key, value)
            except Exception:
                return False

        results = await asyncio.gather(*[_one(b) for b in self._backends.values()])
        return any(results)

    def get_server(self):
        """Return the backend instance for direct access if needed."""
        return self._backend

    def get_listening_host(self) -> KnownHost:
        # Prefer a backend that can return an actual bound socket (e.g., kademlia)
        for backend in self._backends.values():
            try:
                host, port = backend.get_listening_host()
                if host and port:
                    return KnownHost(host, port)
            except Exception:
                continue
        # Fall back to first backend's report
        backend = next(iter(self._backends.values()))
        host, port = backend.get_listening_host()
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
        # Rebuild backend instances from network config
        self._backends = {}
        for cfg in net.backends:
            factory = BACKEND_REGISTRY.get(cfg.backend)
            if factory is None:
                raise ValueError(f"Unsupported DHT backend: {cfg.backend}")
            self._backends[cfg.backend] = factory()
        self._bootstrap_nodes = bootstrap_nodes or net.all_bootstrap_hosts()
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

        manager = DHTManager(bootstrap_nodes=bootstrap_nodes, config=DHTConfig(network=net))
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

        manager = await DHTManager.create(bootstrap_nodes=bootstrap_nodes, config=DHTConfig(network=net))
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
            bootstrap_nodes=bootstrap_nodes or net.all_bootstrap_hosts(),
            config=DHTConfig(network=net),
        )
        self._managers[net.name] = manager
        return manager
