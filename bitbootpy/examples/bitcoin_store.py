"""Example using the Bitcoin backend for simple key/value storage.

Requires ``BITBOOTPY_BTC_KEY`` and ``BITBOOTPY_BTC_RPC_URL`` environment
variables.
"""

import asyncio

from bitbootpy.core.backends.bitcoin_backend import BitcoinBackend


async def main() -> None:
    backend = BitcoinBackend()
    await backend.set(b"hello", b"world")
    print(await backend.get(b"hello"))
    backend.stop()


if __name__ == "__main__":
    asyncio.run(main())
