"""Example using the Solana backend for simple key/value storage.

Requires ``BITBOOTPY_SOLANA_KEYPAIR`` and optionally
``BITBOOTPY_SOLANA_RPC`` environment variables.
"""

import asyncio

from bitbootpy.core.backends.solana_backend import SolanaBackend


async def main() -> None:
    backend = SolanaBackend()
    await backend.set(b"hello", b"world")
    print(await backend.get(b"hello"))
    backend.stop()


if __name__ == "__main__":
    asyncio.run(main())
