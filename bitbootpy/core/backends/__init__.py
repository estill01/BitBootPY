"""Backend registry and built-in backend registrations."""

from __future__ import annotations

from typing import Callable, Dict

from .base import BaseDHTBackend

BACKEND_REGISTRY: Dict[str, Callable[[], BaseDHTBackend]] = {}


def register_backend(name: str, factory: Callable[[], BaseDHTBackend]) -> None:
    """Register a backend factory under ``name``."""
    BACKEND_REGISTRY[name] = factory


# Register built-in backends
from .kademlia import KademliaBackend
from .bitcoin_backend import BitcoinBackend
from .ethereum_backend import EthereumBackend
from .solana_backend import SolanaBackend
from .arweave_backend import ArweaveBackend

register_backend("kademlia", KademliaBackend)
register_backend("btc", BitcoinBackend)
register_backend("eth", EthereumBackend)
register_backend("solana", SolanaBackend)
register_backend("arweave", ArweaveBackend)
