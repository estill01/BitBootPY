"""Example using the Arweave backend for simple key/value storage.

Requires ``BITBOOTPY_ARWEAVE_WALLET`` and optionally
``BITBOOTPY_ARWEAVE_GATEWAY`` environment variables.
"""

import asyncio

from bitbootpy.core.backends.arweave_backend import ArweaveBackend


async def main() -> None:
    backend = ArweaveBackend()
    await backend.set(b"hello", b"world")
    print(await backend.get(b"hello"))
    backend.stop()


if __name__ == "__main__":
    asyncio.run(main())
