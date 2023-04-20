# BitBootPY - Fully-Decentralized Peer Discovery For P2P Networks

# Want to start a decentralized network, but don't know any peer IDs?
# No sweat! BitBootPY has your back.

import hashlib
import time
import libtorrent as lt
from typing import List, Tuple
from tenacity import retry, wait_fixed, stop_after_attempt
import logging

logging.basicConfig(level=logging.INFO)


class DHTManager:
    def __init__(self, bootstrap_nodes: List[Tuple[str, int]] = None):
        settings = lt.settings_pack()
        settings.set_bool(lt.settings_pack.start_default_features, False)
        settings.set_bool(lt.settings_pack.start_default_plugins, False)
        settings.set_bool(lt.settings_pack.start_default_extensions, False)
        settings.set_bool(lt.settings_pack.listen_system_port_fallback, False)
        settings.set_int(lt.settings_pack.listen_interfaces, 0)
        self._session = lt.session(settings)
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

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry_error_callback=lambda _: logging.error("Failed to lookup network"))
    def lookup(self, network_name: str, num_searches: int = 10, delay: int = 5):
        if not network_name:
            raise ValueError("Network name must not be empty.")

        info_hash = self._generate_info_hash(network_name)
        found_peers = set()

        with open("discovered_peers.txt", "w") as f:
            for _ in range(num_searches):
                query = f"get_peers {info_hash.hex()}"
                for node in self._dht_manager._bootstrap_nodes:
                    response = self._dht_manager.get_session().dht_direct_request(query, node)
                    if response and 'values' in response:
                        for peer in response['values']:
                            if peer not in found_peers:
                                found_peers.add(peer)
                                f.write(f"{peer}\n")
                                print(peer)
                                yield peer
                time.sleep(delay)

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry_error_callback=lambda _: logging.error("Failed to announce peer"))
    def announce_peer(self, network_name: str, port: int):
        if not network_name:
            raise ValueError("Network name must not be empty.")
        if not 0 < port <= 65535:
            raise ValueError("Port must be between 1 and 65535.")

        info_hash = self._generate_info_hash(network_name)
        self._dht_manager.get_session().dht_announce(info_hash, port)
