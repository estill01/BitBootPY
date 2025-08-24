"""Example using the Ethereum backend for simple key/value storage.

Requires ``BITBOOTPY_ETH_KEY``, ``BITBOOTPY_ETH_RPC`` and
``BITBOOTPY_ETH_CONTRACT`` environment variables.
"""

import asyncio

from bitbootpy.core.backends.ethereum_backend import EthereumBackend


async def main() -> None:
    backend = EthereumBackend()
    await backend.set(b"hello", b"world")
    print(await backend.get(b"hello"))
    backend.stop()


if __name__ == "__main__":
    asyncio.run(main())
