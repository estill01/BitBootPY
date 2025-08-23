import pytest
from bitbootpy.core.dht_network import (
    add_network,
    remove_network,
    add_known_host,
    remove_known_host,
    DHT_NETWORK_REGISTRY,
    KnownHost,
)


def test_dynamic_known_hosts():
    network = add_network("tempnet")
    host = KnownHost("127.0.0.1", 1234)
    add_known_host(network.name, host)
    assert host in DHT_NETWORK_REGISTRY.get(network.name).bootstrap_hosts
    remove_known_host(network.name, host)
    assert host not in DHT_NETWORK_REGISTRY.get(network.name).bootstrap_hosts
    remove_network(network.name)
    assert DHT_NETWORK_REGISTRY.get(network.name) is None
