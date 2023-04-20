# BitBootPY - Fully-Decentralized Peer Discovery For P2P Networks

# Want to start a decentralized network, but don't know any peer IDs?
# No sweat! BitBootPY has your back.

import hashlib
import time
import libtorrent as lt
from typing import List, Tuple
from tenacity import retry, wait_fixed, stop_after_attempt

class DHTManager:
    def __init__(self, bootstrap_nodes: List[Tuple[str, int]] = None):
        self._session = lt.session()
        self._session.start_dht()
        self._bootstrap_nodes = bootstrap_nodes or [
            ("router.utorrent.com", 6881),
            ("router.bittorrent.com", 6881),
            ("dht.transmissionbt.com", 6881),
            ("dht.aelitis.com", 6881),
        ]
        self._bootstrap_dht()

    def _bootstrap_dht(self):
        for node in self._bootstrap_nodes:
            host, port = node
            self._session.add_dht_bootstrap_node(host, port)

    def stop(self):
        self._session.stop_dht()
        self._session.pause()

    def get_session(self):
        return self._session

class BitBoot:
    def __init__(self):
        self._dht_manager = DHTManager()
        self._discovered_peers = {}

    def __del__(self):
        self._dht_manager.stop()

    def _generate_info_hash(self, network_name: str) -> bytes:
        return hashlib.sha1(network_name.encode()).digest()

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
    def lookup(self, network_name: str, num_searches: int = 10, delay: int = 5) -> set:
        info_hash = self._generate_info_hash(network_name)
        found_peers = set()

        for _ in range(num_searches):
            query = f"get_peers {info_hash.hex()}"
            for node in self._dht_manager._bootstrap_nodes:
                response = self._dht_manager.get_session().dht_direct_request(query, node)
                if response and 'values' in response:
                    found_peers.update(response['values'])
            time.sleep(delay)

        self._discovered_peers[network_name] = found_peers
        return found_peers

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
    def announce_peer(self, network_name: str, port: int):
        info_hash = self._generate_info_hash(network_name)
        self._dht_manager.get_session().dht_announce(info_hash, port)

"""
Example: 

bitboot = BitBoot()

# Announce peer
bitboot.announce_peer("example_network", 6881)

# Discover peers
discovered_peers = bitboot.lookup("example_network")
print("Discovered peers:", discovered_peers)
"""
