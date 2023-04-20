# BitBootPY - Fully-Decentralized Peer Discovery For P2P Networks

# Want to start a decentralized network, but don't know any peer IDs?
# No sweat! BitBootPY has your back.

import hashlib
import time
import libtorrent as lt
from typing import Dict, List, Tuple, Optional
from tenacity import retry, wait_fixed, stop_after_attempt
import logging
import asyncio
import argparse
import sys

logging.basicConfig(level=logging.INFO)


class BitBootConfig:
    def __init__(
        self,
        bootstrap_nodes: Optional[List[Tuple[str, int]]] = None,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        continuous_mode: Optional[Dict[str, bool]] = None,
        network_names: Optional[List[str]] = None,
        print_discovered_peers: bool = True,
    ):
        self.bootstrap_nodes = bootstrap_nodes or [
            ("router.utorrent.com", 6881),
            ("router.bittorrent.com", 6881),
            ("dht.transmissionbt.com", 6881),
            ("dht.aelitis.com", 6881),
        ]
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.continuous_mode = continuous_mode or {}
        self.network_names = network_names or []
        self.print_discovered_peers = print_discovered_peers

    def load_network_names_from_file(self, file_path: str) -> None:
        with open(file_path, "r") as f:
            network_names = [line.strip() for line in f.readlines()]
            self.network_names = network_names

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
    def __init__(
        self,
        config: Optional[BitBootConfig] = None,
        continuous_mode: Optional[Dict[str, bool]] = None,
        network_names: Optional[List[str]] = None,
    ):
        self._config = config or BitBootConfig()
        self._dht_manager = DHTManager(self._config.bootstrap_nodes)

        # Reconcile constructor args with BitBootConfig values
        self._continuous_mode = continuous_mode or self._config.continuous_mode
        self._network_names = network_names or self._config.network_names

        self._discovered_peers = {name: set() for name in self._network_names}


    def __del__(self):
        self._dht_manager.stop()

    # -----------------------
    # Util
    # -----------------------
    def load_network_names_from_file(filename: str) -> List[str]:
        with open(filename, "r") as f:
            return [line.strip() for line in f.readlines()]

    def _generate_info_hash(self, network_name: str) -> bytes:
        return hashlib.sha1(network_name.encode()).digest()

    def num_peers(self) -> Dict[str, int]:
        return {name: len(peers) for name, peers in self._discovered_peers.items()}

    # -----------------------
    # Lookup
    # -----------------------
    async def lookup(self, network_name: str, num_searches: int = 10, delay: int = 5):
        if isinstance(network_names, str):
            network_names = [network_names]

        tasks = []
        for network_name in network_names:
            tasks.append(self._lookup_single(network_name, num_searches, delay))

        await asyncio.gather(*tasks)

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry_error_callback=lambda _: logging.error("Failed to lookup network"))
    async def _lookup_single(self, network_name: str, num_searches: int, delay: int) -> None:
        info_hash = hashlib.sha1(network_name.encode()).digest()
        found_peers = set()

        for _ in range(num_searches):
            await asyncio.sleep(delay)
            results = self._dht_manager.session.dht_get_peers(info_hash)
            if results:
                for peer in results:
                    found_peers.add(peer)

        # Update the discovered peers for this network
        self._discovered_peers[network_name] = found_peers

        # Write discovered peers to a file and print to stdout if enabled
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f"{network_name}_peers.txt", "w") as f:
            for peer in found_peers:
                f.write(f"{peer}\n")
                if self.config.print_discovered_peers:
                    print(f"[{now}] {network_name}: {peer}")


    # -----------------------
    # Announce
    # -----------------------
    async def announce_peer(self, network_names: Union[str, List[str]], port: int):
        if isinstance(network_names, str):
            network_names = [network_names]

        tasks = []
        for network_name in network_names:
            tasks.append(self._announce_peer_single(network_name, port))

        await asyncio.gather(*tasks)


    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry_error_callback=lambda _: logging.error("Failed to announce peer"))
    async def _announce_peer_single(self, network_name: str, port: int) -> None:

        info_hash = hashlib.sha1(network_name.encode()).digest()
        self._dht_manager.session.async_add_torrent({
            "info_hash": lt.sha1_hash(info_hash),
            "flags": lt.torrent_flags.seed_mode | lt.torrent_flags.disable_dht
        })

        # Perform the DHT announce with retries
        for _ in range(self._config.max_retries):
            await asyncio.sleep(self._config.retry_delay)
            self._dht_manager.session.dht_announce(info_hash, port)

    # -----------------------
    # Continuous Mode
    # -----------------------
    async def start_continuous_mode(self, network_name: str):
        if network_name not in self._network_names:
            raise ValueError(f"Network name '{network_name}' is not configured")

        self._continuous_mode[network_name] = True
        while self._continuous_mode[network_name]:
            await self.lookup([network_name])
            await asyncio.sleep(self._config.rate_limit_delay)

    def stop_continuous_mode(self, network_name: str):
        self._continuous_mode[network_name] = False

    def continuous_mode_status(self) -> Dict[str, bool]:
        return self._continuous_mode


# =======================
# CLI
# -----------------------
# =======================

def main(argv: List[str]):
    parser = argparse.ArgumentParser(
        description="BitBoot: A tool for decentralized peer discovery in P2P networks"
    )
    parser.add_argument(
        "-a",
        "--announce",
        metavar="NETWORK_NAME",
        nargs="*",
        help="Announce a peer in the specified network(s)",
    )
    parser.add_argument(
        "-l",
        "--lookup",
        metavar="NETWORK_NAME",
        nargs="*",
        help="Lookup peers in the specified network(s)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=6881,
        help="Port number to announce (default: 6881)",
    )
    parser.add_argument(
        "--continuous",
        metavar="NETWORK_NAME",
        nargs="*",
        help="Enable continuous polling mode for the specified network(s)",
    )
    parser.add_argument(
        "--config",
        metavar="CONFIG_PATH",
        help="Path to a configuration file",
    )
    parser.add_argument(
        "--network-names-file",
        metavar="FILE_PATH",
        help="Load network names from a file (one name per line)",
    )
    parse.add_argument(
       "--print-discovered-peers",
        action="store_true",
        help="Print discovered peers to stdout",
    )

    args = parser.parse_args(argv)

    config = BitBootConfig(print_discovered_peers=args.print_discovered_peers)


    if args.config:
        # Load configuration from the file
        with open(args.config, "r") as f:
            loaded_config = json.load(f)
        config = BitBootConfig(**loaded_config)

    if args.network_names_file:
        config.load_network_names_from_file(args.network_names_file)

    bitboot = BitBoot(config=config)

    async def run_async_tasks():
        tasks = []
        if args.announce:
            for network_name in args.announce:
                tasks.append(bitboot.announce(network_name, args.port))
        if args.lookup:
            for network_name in args.lookup:
                tasks.append(bitboot.lookup(network_name))
        if args.continuous:
            for network_name in args.continuous:
                tasks.append(bitboot.start_continuous_mode(network_name))

        if tasks:
            await asyncio.gather(*tasks)

    if args.announce or args.lookup or args.continuous:
        asyncio.run(run_async_tasks())
    else:
        parser.print_help()

if __name__ == "__main__":
    main(sys.argv[1:])
