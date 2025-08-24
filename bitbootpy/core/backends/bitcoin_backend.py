from __future__ import annotations

"""Lightweight backend that retrieves Bitcoin peer information.

This backend does not implement the full Bitcoin wire protocol.  Instead it
downloads the public list of seed nodes that ships with Bitcoin Core and
exposes them as bootstrap peers.  The backend therefore only supports the
``bootstrap`` step of the :class:`BaseDHTBackend` API.

The implementation intentionally keeps the interface surface small so that the
core package remains lightweight.  Projects that require richer interaction
with the Bitcoin P2P network should replace this backend with a more complete
implementation.
"""

from typing import Any, Iterable, List, Tuple

import httpx

from .base import BaseDHTBackend


class BitcoinBackend(BaseDHTBackend):
    """Retrieve Bitcoin peers from the upstream seed list."""

    SEED_URL = (
        "https://raw.githubusercontent.com/bitcoin/bitcoin/master/contrib/seeds/nodes_main.txt"
    )

    def __init__(self) -> None:
        self._port = 0
        self.nodes: List[Tuple[str, int]] = []

    async def listen(self, port: int) -> None:  # pragma: no cover - network I/O
        self._port = port

    async def bootstrap(
        self, nodes: Iterable[Tuple[str, int]]
    ) -> None:  # pragma: no cover - network I/O
        if nodes:
            self.nodes = list(nodes)
            return

        async with httpx.AsyncClient() as client:
            resp = await client.get(self.SEED_URL, timeout=20)
            resp.raise_for_status()
            lines = resp.text.splitlines()

        discovered: List[Tuple[str, int]] = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Lines are of the form "[ip]:port"; IPv4 addresses are also wrapped
            if line.startswith("[") and "]" in line:
                host, port = line[1:].split("]:")
            else:
                # Fallback, though current seed format always uses brackets
                if ":" not in line:
                    continue
                host, port = line.split(":", 1)
            try:
                discovered.append((host, int(port)))
            except ValueError:
                continue

        self.nodes = discovered

    async def get(self, key: bytes) -> Any:  # pragma: no cover - unsupported
        raise NotImplementedError("Bitcoin backend only supports peer discovery")

    async def set(
        self, key: bytes, value: Any
    ) -> bool:  # pragma: no cover - unsupported
        raise NotImplementedError("Bitcoin backend only supports peer discovery")

    def stop(self) -> None:  # pragma: no cover - illustrative
        pass

    def get_listening_host(self) -> Tuple[str, int]:  # pragma: no cover - network
        return ("0.0.0.0", self._port)


__all__ = ["BitcoinBackend"]

