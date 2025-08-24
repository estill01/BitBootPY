"""Example using the Solana backend for simple key/value storage."""

import asyncio

from bitbootpy.core.dht_manager import DHTManager
from bitbootpy.core.dht_network import DHT_NETWORK_REGISTRY, DHTConfig


async def main() -> None:
    net = DHT_NETWORK_REGISTRY.get("solana")
    manager = await DHTManager.create(config=DHTConfig(network=net))
    await manager.set(b"hello", b"world")
    print(await manager.get(b"hello"))
    manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
