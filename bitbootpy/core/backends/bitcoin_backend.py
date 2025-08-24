from __future__ import annotations

"""Bitcoin backend storing key/value pairs in ``OP_RETURN`` outputs.

This backend embeds BitBootPy data directly into the Bitcoin blockchain by
tagging ``OP_RETURN`` outputs with a unique prefix.  Values are retrieved by
scanning recent blocks for the latest matching entry and stored by
broadcasting a minimal transaction containing the encoded data.

.. warning::
   Publishing data to Bitcoin requires transaction fees and permanently
   reveals the information.  Anyone running this backend must ensure they are
   comfortable with the costs and the public nature of the blockchain.
"""

import asyncio
import os
from typing import Any, Iterable, Tuple

from bitcoin.rpc import RawProxy

from ..wallets import get_bitcoin_key, get_bitcoin_rpc_url
from ..network_names import NetworkName
from .base import BaseDHTBackend
from . import register_backend_with_network


class BitcoinBackend(BaseDHTBackend):
    """Backend that stores BitBootPy records on the Bitcoin blockchain."""

    PREFIX = b"BitBootPy:"

    def __init__(self, rpc_url: str | None = None) -> None:
        self.key = get_bitcoin_key()
        self.rpc_url = rpc_url or get_bitcoin_rpc_url()
        self.proxy = RawProxy(service_url=self.rpc_url)
        self._host: Tuple[str, int] = ("0.0.0.0", 0)
        self._nodes: list[Tuple[str, int]] = []

    async def listen(self, port: int) -> None:  # pragma: no cover - networked
        self._host = ("0.0.0.0", port)

    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:
        """Bootstrap using explicit nodes or fallback DNS seeds."""

        supplied = list(nodes)
        if supplied:
            self._nodes = supplied
            return

        # Only query DNS seeds when no nodes are explicitly supplied.  These
        # seeds operate standard Bitcoin ports.
        seeds = [
            "seed.bitcoin.sipa.be",
            "dnsseed.bluematt.me",
            "seed.bitcoinstats.com",
            "seed.bitcoin.jonasschnelli.ch",
        ]
        self._nodes = [(host, 8333) for host in seeds]

    async def get(self, key: bytes) -> Any:
        """Return the most recent value stored for ``key``.

        The backend scans the last 100 blocks for ``OP_RETURN`` outputs tagged
        with the BitBootPy prefix and returns the latest matching value.
        """

        def _scan() -> Any:
            prefix = self.PREFIX + key + b":"
            best: bytes | None = None
            height = self.proxy.getblockcount()
            start = max(0, height - 100)
            for h in range(height, start, -1):
                blockhash = self.proxy.getblockhash(h)
                block = self.proxy.getblock(blockhash, 2)
                for tx in block.get("tx", []):
                    for vout in tx.get("vout", []):
                        spk = vout.get("scriptPubKey", {})
                        if spk.get("type") == "nulldata":
                            hexdata = spk.get("hex", "")[2:]
                            data = bytes.fromhex(hexdata)
                            if data.startswith(prefix):
                                best = data[len(prefix) :]
                                break
            return best

        return await asyncio.to_thread(_scan)

    async def set(self, key: bytes, value: Any) -> bool:
        """Encode ``key`` and ``value`` in an ``OP_RETURN`` output.

        The transaction is funded by the connected node and signed locally with
        the private key supplied by :func:`get_bitcoin_key`.
        """

        if isinstance(value, bytes):
            value_bytes = value
        elif isinstance(value, str):
            value_bytes = value.encode()
        else:
            value_bytes = str(value).encode()

        payload = (self.PREFIX + key + b":" + value_bytes).hex()

        def _broadcast() -> bool:
            raw = self.proxy.createrawtransaction([], [{"data": payload}])
            funded = self.proxy.fundrawtransaction(raw)["hex"]
            signed = self.proxy.signrawtransactionwithkey(
                funded, [self.key.wif()]
            )["hex"]
            txid = self.proxy.sendrawtransaction(signed)
            return bool(txid)

        return await asyncio.to_thread(_broadcast)

    def stop(self) -> None:  # pragma: no cover - networked
        pass

    def get_listening_host(self) -> Tuple[str, int]:
        return self._host


# Register backend and associated network
register_backend_with_network(NetworkName.BITCOIN, BitcoinBackend, network_name=NetworkName.BITCOIN)

