"""Built-in DHT network definitions."""

from importlib import import_module
from typing import List

_BUILTINS: List[str] = [
    "bittorrent",
    "btc",
    "eth",
    "solana",
    "arweave",
    "local",
]

def register_all() -> None:
    """Import all built-in DHT network modules so they register themselves."""
    for name in _BUILTINS:
        import_module(f"{__name__}.{name}")
