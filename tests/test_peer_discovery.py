import asyncio
import functools
import pytest

# Compatibility shim for libraries expecting ``asyncio.coroutine``

def _compat_coroutine(func):
    if asyncio.iscoroutinefunction(func):
        return func

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


asyncio.coroutine = _compat_coroutine

from bitbootpy.core.bitbootpy import BitBoot, BitBootConfig
from bitbootpy.core.dht_network import KnownHost


class DummyServer:
    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key, [])

    async def set(self, key, value):
        self.store.setdefault(key, []).append(value)
        return True

    async def listen(self, port):
        pass

    async def bootstrap(self, nodes):
        pass

    def stop(self):
        pass


@pytest.mark.asyncio
async def test_peer_discovery_dummy_network():
    dummy = DummyServer()
    node_a = BitBoot()
    node_b = BitBoot()
    node_a._dht_manager.get_manager(node_a._config.dht.network.name)._server = dummy
    node_b._dht_manager.get_manager(node_b._config.dht.network.name)._server = dummy

    peer = KnownHost("127.0.0.1", 1234)
    await node_a.announce_peer("test_topic", peer)
    await node_b.lookup("test_topic", num_searches=1, delay=0)

    discovered = {
        p
        for peers in node_b._discovered_peers["test_topic"].values()
        for p in peers
    }
    assert peer.as_tuple() in discovered

    for mgr in node_a._dht_manager._managers.values():
        mgr.stop()
    for mgr in node_b._dht_manager._managers.values():
        mgr.stop()
