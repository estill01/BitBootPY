# BitBootPY - Fully-Decentralized Peer Discovery For P2P Networks

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Union, Type, TYPE_CHECKING
from tenacity import retry, wait_fixed, stop_after_attempt
import hashlib
import datetime
import logging
import asyncio
from bitbootpy.bitbootpy.dht_manager import DHTManager

if TYPE_CHECKING:
    from bitbootpy.bitbootpy import BitBoot

logging.basicConfig(level=logging.INFO)


# All this needs to do is write to the BT, or some other network's, DHT


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
        self._discovered_peers = {name: set() for name in self._network_names}
        self._network_names = network_names or self._config.network_names

    @classmethod
    async def create(cls,
                     config: Optional[BitBootConfig] = None,
                     continuous_mode: Optional[Dict[str, bool]] = None,
                     network_names: Optional[List[str]] = None
                     ) -> BitBoot:

        instance = cls(config, continuous_mode, network_names)

        instance._dht_manager = yield DHTManager.create(instance._config.bootstrap_nodes)
        # why not just await this?
        instance._bootstrap_dht_task = asyncio.create_task(
            instance._dht_manager._bootstrap_dht())

        return instance

    def __del__(self):
        self._dht_manager.stop()

    # -----------------------
    # Util
    # -----------------------
    async def lookup_and_announce(self, creator: Type[BitBoot], network_name: str, port: int, peer_config: Optional[BitBootConfig] = None) -> None:
        if peer_config is None:
            listening_host, listening_port = creator._dht_manager.get_server(
            ).transport.get_extra_info('sockname')
            peer_config = BitBootConfig(
                bootstrap_nodes=[(listening_host, listening_port)],
                rate_limit_delay=1.0,
                max_retries=3,
                retry_delay=5.0,
            )
        self._config = peer_config
        await self.announce_peer(network_names=[network_name], port=port)
        await self.lookup(network_names=[network_name])

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
            tasks.append(self._lookup_single(
                network_name, num_searches, delay))

        await asyncio.gather(*tasks)

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry_error_callback=lambda _: logging.error("Failed to lookup network"))
    async def _lookup_single(self, network_name: str, num_searches: int, delay: int) -> None:
        info_hash = self._generate_info_hash(network_name)
        found_peers = set()

        for _ in range(num_searches):
            await asyncio.sleep(delay)
            results = await self._dht_manager._server.get(info_hash)
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
        info_hash = self._generate_info_hash(network_name)

        # set for the network name, your IP and port
        host = self._dht_manager.get_server(
        ).transport.get_extra_info('sockname')[0]
        await self._dht_manager._server.set(info_hash, (host, port))

    # -----------------------
    # Continuous Mode
    # -----------------------
    async def start_continuous_mode(self, network_name: str):
        if network_name not in self._network_names:
            raise ValueError(
                f"Network name '{network_name}' is not configured")

        self._continuous_mode[network_name] = True
        while self._continuous_mode[network_name]:
            await self.lookup([network_name])
            await asyncio.sleep(self._config.rate_limit_delay)

    def stop_continuous_mode(self, network_name: str):
        self._continuous_mode[network_name] = False

    def continuous_mode_status(self) -> Dict[str, bool]:
        return self._continuous_mode
