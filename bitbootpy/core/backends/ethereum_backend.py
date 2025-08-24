from __future__ import annotations

import asyncio
import os
from typing import Any, Iterable, Tuple

from web3 import Web3

try:  # discovery v5 is optional
    from ddht import DiscoveryService  # type: ignore
except Exception:  # pragma: no cover - optional
    DiscoveryService = None  # type: ignore

from ..wallets import get_ethereum_key
from ..network_names import NetworkName
from .base import BaseDHTBackend
from . import register_backend_with_network


class EthereumBackend(BaseDHTBackend):
    """Backend storing records in an Ethereum smart contract.

    The backend optionally uses Discovery v5 (via ``ddht``) to maintain a table
    of peers.  If the discovery service is unavailable, contract calls are still
    performed normally.
    """

    ABI = [
        {
            "inputs": [
                {"internalType": "bytes32", "name": "key", "type": "bytes32"}
            ],
            "name": "get",
            "outputs": [
                {"internalType": "bytes", "name": "", "type": "bytes"}
            ],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "bytes32", "name": "key", "type": "bytes32"},
                {"internalType": "bytes", "name": "value", "type": "bytes"},
            ],
            "name": "set",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
    ]

    def __init__(
        self, rpc_url: str | None = None, contract_address: str | None = None
    ) -> None:
        self.key = get_ethereum_key()
        self.rpc_url = rpc_url or os.getenv("BITBOOTPY_ETHEREUM_RPC")
        if not self.rpc_url:
            raise RuntimeError("BITBOOTPY_ETHEREUM_RPC environment variable is not set")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        address = contract_address or os.getenv("BITBOOTPY_ETHEREUM_CONTRACT")
        if not address:
            raise RuntimeError(
                "BITBOOTPY_ETHEREUM_CONTRACT environment variable is not set"
            )
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(address), abi=self.ABI
        )
        self.account = self.key.public_key.to_checksum_address()
        self._host: Tuple[str, int] = ("0.0.0.0", 0)
        self._nodes: list[Tuple[str, int]] = []
        self._discovery = None
        if DiscoveryService is not None:
            try:  # pragma: no cover - networked
                self._discovery = DiscoveryService(self.key.to_bytes())
            except Exception:
                self._discovery = None

    async def listen(self, port: int) -> None:  # pragma: no cover - networked
        self._host = ("0.0.0.0", port)
        if self._discovery is not None:
            try:
                await self._discovery.listen(port)
            except Exception:
                self._discovery = None

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:
        self._nodes = list(nodes)
        if self._discovery is not None:
            for host, udp_port in self._nodes:
                try:
                    self._discovery.add_peer((host, udp_port))
                except Exception:
                    continue

    async def get(self, key: bytes) -> Any:
        key_bytes = key if len(key) == 32 else Web3.keccak(key)

        def _call() -> Any:
            return self.contract.functions.get(key_bytes).call()

        return await asyncio.to_thread(_call)

    async def set(self, key: bytes, value: Any) -> bool:
        key_bytes = key if len(key) == 32 else Web3.keccak(key)
        if isinstance(value, bytes):
            data = value
        elif isinstance(value, str):
            data = value.encode()
        else:
            data = str(value).encode()

        def _send() -> bool:
            tx = self.contract.functions.set(key_bytes, data).build_transaction(
                {
                    "from": self.account,
                    "nonce": self.w3.eth.get_transaction_count(self.account),
                    "gas": 200000,
                    "gasPrice": self.w3.eth.gas_price,
                }
            )
            signed = self.w3.eth.account.sign_transaction(
                tx, private_key=self.key.to_bytes()
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt.status == 1

        return await asyncio.to_thread(_send)

    def stop(self) -> None:  # pragma: no cover - networked
        if self._discovery is not None:
            try:
                self._discovery.stop()
            except Exception:
                pass

    def get_listening_host(self) -> Tuple[str, int]:
        return self._host


# Register backend and associated network
register_backend_with_network(NetworkName.ETHEREUM, EthereumBackend, network_name=NetworkName.ETHEREUM)
