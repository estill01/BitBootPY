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


class BitBootConfig:
    def __init__(self, bootstrap_nodes=None, rate_limit_delay=1.0, max_retries=3, retry_delay=5.0):
        self.bootstrap_nodes = bootstrap_nodes or [
            ("router.utorrent.com", 6881),
            ("router.bittorrent.com", 6881),
            ("dht.transmissionbt.com", 6881),
            ("dht.aelitis.com", 6881),
        ]
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.retry_delay = retry_delay


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
    def __init__(self, config=None):
        self._config = config or BitBootConfig()
        self._dht_manager = DHTManager(self._config.bootstrap_nodes)
        self._discovered_peers = {}
        self._continuous_mode = False

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
    async def _lookup_single(self, network_name: str, num_searches: int, delay: int):
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

        # Write discovered peers to a file
        with open(f"{network_name}_peers.txt", "w") as f:
            for peer in found_peers:
                f.write(f"{peer}\n")
                print(f"Discovered peer: {peer}")


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
    async def _announce_peer_single(self, network_name: str, port: int):
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
    async def start_continuous_mode(self, network_names: List[str]):
        self._continuous_mode = True
        while self._continuous_mode:
            await self.lookup(network_names)
            await asyncio.sleep(self._config.rate_limit_delay)

    def stop_continuous_mode(self):
        self._continuous_mode = False



def main():
    parser = argparse.ArgumentParser(description="BitBoot Peer Discovery")
    parser.add_argument("network_names", nargs="*", help="The names of the networks you want to announce or lookup")
    parser.add_argument("-f", "--file", help="Load network names from a file")
    parser.add_argument("-a", "--announce", action="store_true", help="Announce a peer in the specified networks")
    parser.add_argument("-l", "--lookup", action="store_true", help="Lookup peers in the specified networks")
    parser.add_argument("-p", "--port", type=int, help="The port to use when announcing a peer (required for -a)")
    parser.add_argument("-c", "--continuous", action="store_true", help="Run in continuous polling mode")

    args = parser.parse_args()

    if not (args.announce or args.lookup):
        parser.error("At least one of -a/--announce or -l/--lookup is required")

    if args.announce and not args.port:
        parser.error("The -p/--port option is required when announcing a peer")

    network_names = args.network_names

    if args.file:
        network_names.extend(load_network_names_from_file(args.file))

    if not network_names:
        parser.error("No network names provided. Provide them as arguments or use -f/--file option")

    bitboot = BitBoot()

    if args.continuous:
        print("Running in continuous polling mode")

    while True:
        if args.announce:
        asyncio.run(bitboot.announce_peer(network_names, args.port))
        print(f"Announced peer for networks {network_names} on port {args.port}")

        if args.lookup:
        print(f"Looking up peers for networks {network_names}:")
        asyncio.run(bitboot.lookup(network_names))

        if not args.continuous:
        break

        print(f"Waiting {bitboot._config.rate_limit_delay} seconds before polling again")
        time.sleep(bitboot._config.rate_limit_delay)


    if args.announce:
        asyncio.run(bitboot.announce_peer(network_names, args.port))
        print(f"Announced peer for networks {network_names} on port {args.port}")

    if args.lookup:
        print(f"Looking up")

if __name__ == "__main__":
    main()
