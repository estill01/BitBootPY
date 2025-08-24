from bitbootpy.core.dht_network import (
    add_network,
    remove_network,
    add_known_host,
    remove_known_host,
    DHT_NETWORK_REGISTRY,
    KnownHost,
)
from bitbootpy.core.backends import BACKEND_REGISTRY
from bitbootpy.core.network_names import NetworkName


def test_dynamic_known_hosts():
    network = add_network("tempnet")
    host = KnownHost("127.0.0.1", 1234)
    add_known_host(network.name, host)
    assert host in DHT_NETWORK_REGISTRY.get(network.name).bootstrap_hosts
    remove_known_host(network.name, host)
    assert host not in DHT_NETWORK_REGISTRY.get(network.name).bootstrap_hosts
    remove_network(network.name)
    assert DHT_NETWORK_REGISTRY.get(network.name) is None


def test_builtin_networks_registered():
    # built-in networks register with canonical names
    assert DHT_NETWORK_REGISTRY.get(NetworkName.BITCOIN) is not None
    assert NetworkName.BITCOIN in BACKEND_REGISTRY
