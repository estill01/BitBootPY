from __future__ import annotations

"""Backend retrieving Arweave peers via the public HTTP API."""

from typing import Any, Iterable, List, Tuple

import httpx

from .base import BaseDHTBackend


class ArweaveBackend(BaseDHTBackend):
    """Fetch peers from ``https://arweave.net/peers``."""

    PEERS_URL = "https://arweave.net/peers"

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
            resp = await client.get(self.PEERS_URL, timeout=20)
            resp.raise_for_status()
            peers = resp.json()

        # Arweave peers are returned as hostnames; default port is 1984
        self.nodes = [(host, 1984) for host in peers]

    async def get(self, key: bytes) -> Any:  # pragma: no cover - unsupported
        raise NotImplementedError("Arweave backend only supports peer discovery")

    async def set(
        self, key: bytes, value: Any
    ) -> bool:  # pragma: no cover - unsupported
        raise NotImplementedError("Arweave backend only supports peer discovery")

    def stop(self) -> None:  # pragma: no cover
        pass

    def get_listening_host(self) -> Tuple[str, int]:  # pragma: no cover
        return ("0.0.0.0", self._port)


__all__ = ["ArweaveBackend"]

