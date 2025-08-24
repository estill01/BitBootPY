from __future__ import annotations

"""Placeholder backend for the Solana network.

This backend does not implement actual Solana peer discovery.  It merely
illustrates how a third-party library could be wrapped to conform to the
:class:`BaseDHTBackend` interface.
"""

from typing import Any, Iterable, Tuple

from ..wallets import get_solana_keypair
from .base import BaseDHTBackend


class SolanaBackend(BaseDHTBackend):
    """Non-functional example backend for the Solana network."""

    def __init__(self) -> None:
        # Load the Solana keypair from the environment to identify the node.
        self.keypair = get_solana_keypair()

    async def listen(self, port: int) -> None:  # pragma: no cover - illustrative
        raise NotImplementedError("Solana backend not implemented")

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:  # pragma: no cover - illustrative
        raise NotImplementedError("Solana backend not implemented")

    async def get(self, key: bytes) -> Any:  # pragma: no cover - illustrative
        raise NotImplementedError("Solana backend not implemented")

    async def set(self, key: bytes, value: Any) -> bool:  # pragma: no cover - illustrative
        raise NotImplementedError("Solana backend not implemented")

    def stop(self) -> None:  # pragma: no cover - illustrative
        pass

    def get_listening_host(self) -> Tuple[str, int]:  # pragma: no cover - illustrative
        raise NotImplementedError("Solana backend not implemented")
