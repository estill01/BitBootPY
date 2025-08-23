"""Example showing how to register and use a custom DHT backend."""

import asyncio
from typing import Iterable, Tuple, Any

from bitbootpy.core.backends import BACKEND_REGISTRY, BaseDHTBackend
from bitbootpy.core.dht_network import DHT_NETWORK_REGISTRY, DHTNetwork, DHTConfig
from bitbootpy.core.dht_manager import DHTManager


class InMemoryBackend(BaseDHTBackend):
    """Trivial backend storing values in a local dictionary.

    This backend is not distributed; it merely demonstrates how a backend fits
    into the BitBootPy architecture.  Two peers using this backend would need to
    share the same Python object to communicate.
    """

    def __init__(self) -> None:
        self.store = {}
        self.addr = ("127.0.0.1", 0)

    async def listen(self, port: int) -> None:
        self.addr = ("127.0.0.1", port)

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:
        pass

    async def get(self, key: bytes) -> Any:
        return self.store.get(key)

    async def set(self, key: bytes, value: Any) -> bool:
        self.store[key] = value
        return True

    def stop(self) -> None:
        pass

    def get_listening_host(self) -> Tuple[str, int]:
        return self.addr


async def main() -> None:
    BACKEND_REGISTRY["inmemory"] = InMemoryBackend
    net = DHT_NETWORK_REGISTRY.add(DHTNetwork("demo", backend="inmemory"))
    manager = await DHTManager.create(config=DHTConfig(network=net))
    await manager.set(b"hello", "world")
    print(await manager.get(b"hello"))
    manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
