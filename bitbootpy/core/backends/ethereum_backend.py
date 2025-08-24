from __future__ import annotations

"""Backend that fetches Ethereum bootnodes via HTTP.

The backend scrapes the list of well-known bootnodes published in the
`go-ethereum` repository.  It only provides peer discovery and does not expose
the Discovery v5 protocol for key/value operations.
"""

from typing import Any, Iterable, List, Tuple

import httpx

from .base import BaseDHTBackend


class EthereumBackend(BaseDHTBackend):
    """Fetch Ethereum bootnodes from the go-ethereum repository."""

    BOOTNODES_URL = (
        "https://raw.githubusercontent.com/ethereum/go-ethereum/master/params/bootnodes.go"
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
            resp = await client.get(self.BOOTNODES_URL, timeout=20)
            resp.raise_for_status()
            content = resp.text

        discovered: List[Tuple[str, int]] = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("\"enode://"):
                # Example: "enode://pubkey@ip:port", // comment
                try:
                    uri = line.split("\"")[1]
                    host_port = uri.split("@", 1)[1]
                    host, port = host_port.split(":")
                    discovered.append((host, int(port)))
                except Exception:
                    continue

        self.nodes = discovered

    async def get(self, key: bytes) -> Any:  # pragma: no cover - unsupported
        raise NotImplementedError("Ethereum backend only supports peer discovery")

    async def set(
        self, key: bytes, value: Any
    ) -> bool:  # pragma: no cover - unsupported
        raise NotImplementedError("Ethereum backend only supports peer discovery")

    def stop(self) -> None:  # pragma: no cover - illustrative
        pass

    def get_listening_host(self) -> Tuple[str, int]:  # pragma: no cover
        return ("0.0.0.0", self._port)


__all__ = ["EthereumBackend"]

