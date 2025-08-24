from __future__ import annotations

"""Enumerations of built-in network identifiers.

The project historically referenced networks by string name.  This module
introduces :class:`NetworkName` which enumerates the canonical names used across
BitBootPy.  Using an ``Enum`` provides a fully specified way to select networks
while still behaving like ``str`` for backward compatibility.
"""

from enum import Enum


class NetworkName(str, Enum):
    """Canonical identifiers for built-in networks."""

    BIT_TORRENT = "bit_torrent"
    LOCAL = "local"
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    SOLANA = "solana"
    ARWEAVE = "arweave"

