import asyncio
import functools
import pytest

from bitbootpy.core.network_names import NetworkName

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
from bitbootpy.core.dht_network import (
    KnownHost,
    DHT_NETWORK_REGISTRY,
    DHTConfig,
)
from bitbootpy.core.network import NETWORK_REGISTRY


class DummyBackend:
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

    def get_listening_host(self):
        return ("127.0.0.1", 0)


@pytest.mark.asyncio
async def test_peer_discovery_dummy_network():
    dummy = DummyBackend()
    local_net = DHT_NETWORK_REGISTRY.get(NetworkName.LOCAL)
    test_network = NETWORK_REGISTRY.create("test_topic", [local_net])
    config_a = BitBootConfig(dht=DHTConfig(network=local_net))
    config_b = BitBootConfig(dht=DHTConfig(network=local_net))
    node_a = BitBoot(config=config_a)
    node_b = BitBoot(config=config_b)
    node_a._dht_manager.get_manager(local_net.name)._backend = dummy
    node_b._dht_manager.get_manager(local_net.name)._backend = dummy

    peer = KnownHost("127.0.0.1", 1234)
    await node_a.announce_peer(test_network, peer)
    await node_b.lookup(test_network, num_searches=1, delay=0)

    discovered = {
        p for peers in node_b._discovered_peers[test_network.name].values() for p in peers
    }
    assert peer.as_tuple() in discovered

    for mgr in node_a._dht_manager._managers.values():
        mgr.stop()
    for mgr in node_b._dht_manager._managers.values():
        mgr.stop()
