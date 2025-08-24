"""Basic example showing how to store and retrieve a value."""

import asyncio

from bitbootpy import BitBoot, BitBootConfig


async def main() -> None:
    bitboot = await BitBoot.create(BitBootConfig())
    manager = bitboot._dht_manager.get_manager(bitboot._config.dht.network.name)
    await manager.set(b"example-key", b"example-value")
    value = await manager.get(b"example-key")
    print("Retrieved:", value)


if __name__ == "__main__":
    asyncio.run(main())
