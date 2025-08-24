"""Retrieve Arweave peers using the HTTP backend."""

import asyncio

from bitbootpy.core.dht_network import DHT_NETWORK_REGISTRY, DHTConfig
from bitbootpy.core.dht_manager import DHTManager


async def main() -> None:
    network = DHT_NETWORK_REGISTRY.get("arweave")
    manager = await DHTManager.create(config=DHTConfig(network=network))
    backend = manager.get_server()
    print("discovered", len(backend.nodes), "peers")
    for peer in backend.nodes[:5]:
        print(" ", peer)
    manager.stop()


if __name__ == "__main__":
    asyncio.run(main())

