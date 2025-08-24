from __future__ import annotations

"""Arweave backend storing key/value pairs as transactions."""

import asyncio
import base64
import json
import os
import urllib.request
from typing import Any, Iterable, Tuple, List

from arweave import Transaction

from ..wallets import get_arweave_wallet
from .base import BaseDHTBackend


class ArweaveBackend(BaseDHTBackend):
    """Backend that stores BitBootPy records on the Arweave blockchain."""

    TAG_NAME = "BitBootPy-Key"

    def __init__(self, gateway_url: str | None = None) -> None:
        self.wallet = get_arweave_wallet()
        self.gateway_url = gateway_url or os.getenv(
            "BITBOOTPY_ARWEAVE_GATEWAY", "https://arweave.net"
        )
        self._host: Tuple[str, int] = ("0.0.0.0", 0)
        self._nodes: List[Tuple[str, int]] = []

    async def listen(self, port: int) -> None:
        self._host = ("0.0.0.0", port)

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:
        self._nodes = list(nodes)

    async def get(self, key: bytes) -> Any:
        key_tag = base64.b64encode(key).decode()

        def _query() -> Any:
            q = {
                "query": (
                    "query($key:String!){" "transactions(tags:[{name:\"%s\",values:[$key]}],sort:HEIGHT_DESC,first:1){" "edges{node{id}}}}"
                    % self.TAG_NAME
                ),
                "variables": {"key": key_tag},
            }
            data = json.dumps(q).encode()
            req = urllib.request.Request(
                self.gateway_url.rstrip("/") + "/graphql",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as resp:
                result = json.load(resp)
            edges = result.get("data", {}).get("transactions", {}).get("edges", [])
            if not edges:
                return None
            tx_id = edges[0]["node"]["id"]
            with urllib.request.urlopen(
                self.gateway_url.rstrip("/") + "/" + tx_id
            ) as resp:
                return resp.read()

        return await asyncio.to_thread(_query)

    async def set(self, key: bytes, value: Any) -> bool:
        if isinstance(value, bytes):
            data = value
        elif isinstance(value, str):
            data = value.encode()
        else:
            data = str(value).encode()
        key_tag = base64.b64encode(key).decode()

        def _send() -> bool:
            tx = Transaction(self.wallet, data=data)
            tx.add_tag(self.TAG_NAME, key_tag)
            tx.sign()
            tx.send()
            return True

        return await asyncio.to_thread(_send)

    def stop(self) -> None:
        pass

    def get_listening_host(self) -> Tuple[str, int]:
        return self._host
