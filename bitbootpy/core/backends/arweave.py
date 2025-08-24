from __future__ import annotations

"""Arweave backend storing values on the Arweave permaweb."""

import asyncio
import os
from typing import Any, Iterable, List, Tuple

import requests
from arweave import Transaction

from ..wallets import get_arweave_wallet
from .base import BaseDHTBackend


class ArweaveBackend(BaseDHTBackend):
    """Backend that persists key/value pairs to Arweave."""

    def __init__(self, gateway: str | None = None) -> None:
        self.wallet = get_arweave_wallet()
        env_gateway = os.getenv("BITBOOTPY_ARWEAVE_GATEWAY")
        self.gateway = gateway or env_gateway or "https://arweave.net"
        self.wallet.api_url = self.gateway
        self.gateways: List[str] = [self.gateway]
        self._host: Tuple[str, int] = ("0.0.0.0", 0)

    async def listen(self, port: int) -> None:  # pragma: no cover - networked
        self._host = ("0.0.0.0", port)

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:
        """Optionally configure a list of gateway URLs."""
        gateways: List[str] = []
        for host, port in nodes:
            if host.startswith("http://") or host.startswith("https://"):
                url = host.rstrip("/")
            else:
                url = f"http://{host}:{port}" if port else f"http://{host}"
            gateways.append(url)
        if gateways:
            self.gateways = gateways
            self.gateway = gateways[0]
            self.wallet.api_url = self.gateway

    async def set(self, key: bytes, value: Any) -> bool:
        """Store ``value`` under ``key`` by posting a signed transaction."""
        key_str = key.decode() if isinstance(key, bytes) else str(key)
        if isinstance(value, bytes):
            data = value
        elif isinstance(value, str):
            data = value.encode()
        else:
            data = str(value).encode()

        def _send() -> bool:
            tx = Transaction(self.wallet, data=data)
            tx.api_url = self.gateway
            tx.add_tag("BitBootKey", key_str)
            tx.sign()
            tx.send()
            return True

        return await asyncio.to_thread(_send)

    async def get(self, key: bytes) -> Any:
        """Retrieve the most recent value stored for ``key``."""
        key_str = key.decode() if isinstance(key, bytes) else str(key)
        url = f"{self.gateway}/graphql"

        def _fetch() -> Any:
            query = {
                "query": (
                    "query($value:String!){transactions(tags:[{name:\"BitBootKey\", values:[$value]}],"
                    " first:1, sort:HEIGHT_DESC){edges{node{id}}}}"
                ),
                "variables": {"value": key_str},
            }
            resp = requests.post(url, json=query)
            if resp.status_code != 200:
                return None
            edges = resp.json().get("data", {}).get("transactions", {}).get("edges", [])
            if not edges:
                return None
            txid = edges[0]["node"]["id"]
            data_resp = requests.get(f"{self.gateway}/{txid}")
            if data_resp.status_code != 200:
                return None
            return data_resp.content

        return await asyncio.to_thread(_fetch)

    def stop(self) -> None:  # pragma: no cover - networked
        pass

    def get_listening_host(self) -> Tuple[str, int]:
        return self._host
