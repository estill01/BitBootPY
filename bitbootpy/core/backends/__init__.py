"""Backend registry and helper for registering networks alongside backends.

This module acts as the single entry-point for backend registration. Backends
register themselves under a clear, normalized key (e.g. "kademlia",
"bitcoin", "ethereum", "solana", "arweave"). Networks are registered
separately and can be re-pointed to a different backend at runtime.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Union

from ..dht_network import (
    DHTNetwork,
    DHTBackendConfig,
    DHT_NETWORK_REGISTRY,
    KnownHost,
)
from ..network_names import NetworkName
from .base import BaseDHTBackend

# ---------------------------------------------------------------------------
# Backend registry
# ---------------------------------------------------------------------------

BACKEND_REGISTRY: Dict[str, Callable[[], BaseDHTBackend]] = {}


def register_backend_with_network(
    backend_name: Union[NetworkName, str],
    backend_factory: Callable[[], BaseDHTBackend],
    network_name: Optional[Union[NetworkName, str]] = None,
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

    # Normalize keys to plain strings
    backend_key = (
        backend_name.value if isinstance(backend_name, NetworkName) else str(backend_name)
    )
    network = (
        network_name.value if isinstance(network_name, NetworkName) else str(network_name or backend_key)
    )
    BACKEND_REGISTRY[backend_key] = backend_factory

    # Append or create network with the given backend mapping
    existing = DHT_NETWORK_REGISTRY.get(network)
    cfg = DHTBackendConfig(backend=backend_key, bootstrap_hosts=bootstrap_hosts or [])
    if existing is None:
        DHT_NETWORK_REGISTRY.add(DHTNetwork(name=network, backends=[cfg]))
    else:
        # Replace existing config for this backend if present; else append
        replaced = False
        for i, b in enumerate(existing.backends):
            if b.backend == backend_key:
                existing.backends[i] = cfg
                replaced = True
                break
        if not replaced:
            existing.backends.append(cfg)


def set_backend_for_network(
    network_name: Union[str, NetworkName], backend_key: str
) -> None:
    """Point an existing network to a different backend.

    This enables quick switching between implementations for the same logical
    network name without any backwards-compat nuances.
    """
    key = network_name.value if isinstance(network_name, NetworkName) else str(network_name)
    network = DHT_NETWORK_REGISTRY.get(key)
    if not network:
        # Create the network if it doesn't exist yet with empty hosts
        DHT_NETWORK_REGISTRY.add(
            DHTNetwork(name=key, backends=[DHTBackendConfig(backend_key, [])])
        )
        return
    # Preserve union of hosts and set a single backend
    hosts = network.all_bootstrap_hosts()
    new_net = DHTNetwork(name=network.name, backends=[DHTBackendConfig(backend_key, hosts)])
    DHT_NETWORK_REGISTRY.add(new_net)


# ---------------------------------------------------------------------------
# Import built-in backends so they register themselves
# ---------------------------------------------------------------------------

from . import kademlia  # noqa: F401

try:  # pragma: no cover - illustrative only
    from . import arweave_backend  # noqa: F401
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
