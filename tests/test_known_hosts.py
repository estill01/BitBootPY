import pytest
from bitbootpy.core.known_hosts import (
    add_network,
    remove_network,
    add_known_host,
    remove_known_host,
    KNOWN_HOSTS,
    KnownHost,
)


def test_dynamic_known_hosts():
    network = add_network("tempnet")
    host = KnownHost("127.0.0.1", 1234)
    add_known_host(network, host)
    assert host in KNOWN_HOSTS[network]
    remove_known_host(network, host)
    assert host not in KNOWN_HOSTS[network]
    remove_network(network)
    assert network not in KNOWN_HOSTS
