from __future__ import annotations

"""Placeholder backend for Ethereum's Discovery v5 protocol.

The implementation here is intentionally minimal and serves primarily as an
example of how a backend could be wired into BitBootPy.  A fully working
backend would likely wrap an external library that implements the Discovery v5
protocol.
"""

from typing import Any, Iterable, Tuple

from .base import BaseDHTBackend


class EthereumDiscv5Backend(BaseDHTBackend):
    """Non-functional example backend for Ethereum Discovery v5."""

    async def listen(self, port: int) -> None:  # pragma: no cover - illustrative
        raise NotImplementedError("Ethereum Discovery v5 backend not implemented")

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:  # pragma: no cover - illustrative
        raise NotImplementedError("Ethereum Discovery v5 backend not implemented")

    async def get(self, key: bytes) -> Any:  # pragma: no cover - illustrative
        raise NotImplementedError("Ethereum Discovery v5 backend not implemented")

    async def set(self, key: bytes, value: Any) -> bool:  # pragma: no cover - illustrative
        raise NotImplementedError("Ethereum Discovery v5 backend not implemented")

    def stop(self) -> None:  # pragma: no cover - illustrative
        pass

    def get_listening_host(self) -> Tuple[str, int]:  # pragma: no cover - illustrative
        raise NotImplementedError("Ethereum Discovery v5 backend not implemented")
