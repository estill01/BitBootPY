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
register_backend("kademlia", KademliaBackend)

# Optional example backends
try:  # pragma: no cover - illustrative only
    from .ethereum_discv5 import EthereumDiscv5Backend

    register_backend("eth-discv5", EthereumDiscv5Backend)
except Exception:  # pragma: no cover - illustrative only
    pass

try:  # pragma: no cover - illustrative only
    from .solana_backend import SolanaBackend

    register_backend("solana", SolanaBackend)
except Exception:  # pragma: no cover - illustrative only
    pass

try:  # pragma: no cover - illustrative only
    from .bitcoin_backend import BitcoinBackend

    register_backend("bitcoin", BitcoinBackend)
except Exception:  # pragma: no cover - illustrative only
    pass
