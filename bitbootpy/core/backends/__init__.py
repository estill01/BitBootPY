"""Backend registry and helper for registering networks alongside backends."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from ..dht_network import DHTNetwork, DHT_NETWORK_REGISTRY, KnownHost
from .base import BaseDHTBackend

# ---------------------------------------------------------------------------
# Backend registry
# ---------------------------------------------------------------------------

BACKEND_REGISTRY: Dict[str, Callable[[], BaseDHTBackend]] = {}


def register_backend_with_network(
    backend_name: str,
    backend_factory: Callable[[], BaseDHTBackend],
    network_name: Optional[str] = None,
    bootstrap_hosts: Optional[List[KnownHost]] = None,
) -> None:
    """Register ``backend_factory`` and an optional associated network.

    Parameters
    ----------
    backend_name:
        Name under which the backend factory will be stored.
    backend_factory:
        Callable returning an instance of :class:`BaseDHTBackend`.
    network_name:
        Optional name of a :class:`~bitbootpy.core.dht_network.DHTNetwork` to
        register simultaneously.  If omitted, ``backend_name`` is used.
    bootstrap_hosts:
        Optional list of :class:`KnownHost` entries describing bootstrap nodes
        for the network.
    """

    BACKEND_REGISTRY[backend_name] = backend_factory

    DHT_NETWORK_REGISTRY.add(
        DHTNetwork(
            network_name or backend_name,
            backend=backend_name,
            bootstrap_hosts=bootstrap_hosts or [],
        )
    )


# ---------------------------------------------------------------------------
# Import built-in backends so they register themselves
# ---------------------------------------------------------------------------

from . import kademlia  # noqa: F401

try:  # pragma: no cover - illustrative only
    from . import arweave  # noqa: F401
except Exception:  # pragma: no cover - illustrative only
    pass

try:  # pragma: no cover - illustrative only
    from . import ethereum_backend  # noqa: F401
except Exception:  # pragma: no cover - illustrative only
    pass

try:  # pragma: no cover - illustrative only
    from . import solana_backend  # noqa: F401
except Exception:  # pragma: no cover - illustrative only
    pass

try:  # pragma: no cover - illustrative only
    from . import bitcoin_backend  # noqa: F401
except Exception:  # pragma: no cover - illustrative only
    pass
