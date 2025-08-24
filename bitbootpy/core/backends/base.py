from __future__ import annotations

"""Abstract base class for pluggable DHT backends.

Backends are lightweight wrappers around third-party libraries that provide
basic DHT functionality.  Each backend must implement a small async API so the
:class:`~bitbootpy.core.dht_manager.DHTManager` can interact with it without
knowing any backend specifics.
"""

from abc import ABC, abstractmethod
from typing import Any, Iterable, Tuple


class BaseDHTBackend(ABC):
    """Minimal interface all DHT backends must implement."""

    @abstractmethod
    async def listen(self, port: int) -> None:
        """Start listening on the given UDP/TCP port."""

    @abstractmethod
    async def bootstrap(self, nodes: Iterable[Tuple[str, int]]) -> None:
        """Bootstrap the DHT using a list of known nodes."""

    @abstractmethod
    async def get(self, key: bytes) -> Any:
        """Retrieve a value for ``key`` from the DHT."""

    @abstractmethod
    async def set(self, key: bytes, value: Any) -> bool:
        """Store a value for ``key`` on the DHT."""

    @abstractmethod
    def stop(self) -> None:
        """Shut down the backend and release all resources."""

    @abstractmethod
    def get_listening_host(self) -> Tuple[str, int]:
        """Return the address the backend is listening on."""
