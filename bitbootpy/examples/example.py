"""Basic example demonstrating announcing and looking up peers."""

import asyncio

from bitbootpy import BitBoot, BitBootConfig, KnownHost


async def main() -> None:
    bitboot = await BitBoot.create(BitBootConfig())
    await bitboot.announce_peer("example_network", KnownHost("127.0.0.1", 6881))
    await bitboot.lookup("example_network")


if __name__ == "__main__":
    asyncio.run(main())


