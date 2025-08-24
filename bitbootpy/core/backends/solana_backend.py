from __future__ import annotations

"""Solana backend storing key/value pairs in on-chain accounts.

This backend uses the ``solana-py`` library to create or update accounts whose
addresses are derived from the provided key.  Values are stored directly in the
account data.  Peer discovery is not provided beyond optional gossip via the
``bootstrap`` method to mirror other backends.
"""

import base64
import base58
import os
from typing import Any, Iterable, Tuple, List

from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction, Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders import system_program as sp

from ..wallets import get_solana_keypair
from .base import BaseDHTBackend


class SolanaBackend(BaseDHTBackend):
    """Backend that stores BitBootPy records on the Solana blockchain."""

    def __init__(self, rpc_url: str | None = None) -> None:
        self.keypair = get_solana_keypair()
        self.rpc_url = rpc_url or os.getenv(
            "BITBOOTPY_SOLANA_RPC", "https://api.mainnet-beta.solana.com"
        )
        self.client = AsyncClient(self.rpc_url)
        self._host: Tuple[str, int] = ("0.0.0.0", 0)
        self._nodes: List[Tuple[str, int]] = []

    async def listen(self, port: int) -> None:
        self._host = ("0.0.0.0", port)

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:
        """Record optional gossip nodes for peer discovery."""

        self._nodes = list(nodes)

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _derive_address(self, key: bytes) -> Tuple[Pubkey, str]:
        seed = base58.b58encode(key).decode()[:32]
        base = self.keypair.pubkey()
        addr = Pubkey.create_with_seed(base, seed, sp.ID)
        return addr, seed

    # ------------------------------------------------------------------
    # Backend API implementation
    # ------------------------------------------------------------------
    async def get(self, key: bytes) -> Any:
        addr, _ = self._derive_address(key)
        resp = await self.client.get_account_info(addr)
        value = resp.value
        if value is None:
            return None
        data = value.data[0] if hasattr(value, "data") else value["data"][0]
        return base64.b64decode(data)

    async def set(self, key: bytes, value: Any) -> bool:
        if isinstance(value, bytes):
            data = value
        elif isinstance(value, str):
            data = value.encode()
        else:
            data = str(value).encode()

        addr, seed = self._derive_address(key)
        existing = await self.client.get_account_info(addr)
        tx = Transaction()
        lamports = await self.client.get_minimum_balance_for_rent_exemption(len(data))
        if existing.value is None:
            params = sp.CreateAccountWithSeedParams(
                from_pubkey=self.keypair.pubkey(),
                to_pubkey=addr,
                base=self.keypair.pubkey(),
                seed=seed,
                lamports=lamports.value if hasattr(lamports, "value") else lamports,
                space=len(data),
                owner=sp.ID,
            )
            tx.add(sp.create_account_with_seed(params))
        # Write the value as raw account data.  This uses a generic instruction to
        # the system program which simply stores ``data`` in the account.
        tx.add(
            Instruction(
                program_id=sp.ID,
                data=data,
                accounts=[AccountMeta(pubkey=addr, is_signer=False, is_writable=True)],
            )
        )
        await self.client.send_transaction(tx, self.keypair)
        return True

    def stop(self) -> None:
        if self.client:
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.client.close())
                else:
                    loop.run_until_complete(self.client.close())
            except Exception:
                pass

    def get_listening_host(self) -> Tuple[str, int]:
        return self._host
