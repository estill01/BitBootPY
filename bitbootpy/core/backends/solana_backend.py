from __future__ import annotations

"""Backend retrieving Solana cluster nodes via JSON-RPC."""

from typing import Any, Iterable, List, Tuple

import httpx

from .base import BaseDHTBackend


class SolanaBackend(BaseDHTBackend):
    """Fetch peers from the public Solana RPC endpoint."""

    RPC_URL = "https://api.mainnet-beta.solana.com"

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

        payload = {"jsonrpc": "2.0", "id": 1, "method": "getClusterNodes"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.RPC_URL, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()

        discovered: List[Tuple[str, int]] = []
        for entry in data.get("result", []):
            gossip = entry.get("gossip")
            if not gossip:
                continue
            try:
                host, port = gossip.split(":")
                discovered.append((host, int(port)))
            except Exception:
                continue

        self.nodes = discovered

    async def get(self, key: bytes) -> Any:  # pragma: no cover - unsupported
        raise NotImplementedError("Solana backend only supports peer discovery")

    async def set(
        self, key: bytes, value: Any
    ) -> bool:  # pragma: no cover - unsupported
        raise NotImplementedError("Solana backend only supports peer discovery")

    def stop(self) -> None:  # pragma: no cover
        pass

    def get_listening_host(self) -> Tuple[str, int]:  # pragma: no cover
        return ("0.0.0.0", self._port)


__all__ = ["SolanaBackend"]

