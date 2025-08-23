# BitBootPY - Fully-Decentralized Peer Discovery For P2P Networks

from __future__ import annotations

from typing import Dict, List, Optional, Union, Type
from tenacity import retry, wait_fixed, stop_after_attempt
import hashlib
import datetime
import logging
import asyncio
from .dht_manager import DHTManager, MultiDHTManager
from .dht_network import (
    KnownHost,
    DHTConfig,
    DHTNetwork,
    DHT_NETWORK_REGISTRY,
)
from .network import Network, NETWORK_REGISTRY

logging.basicConfig(level=logging.INFO)


# All this needs to do is write to the BT, or some other network's, DHT


class BitBootConfig:
    def __init__(
        self,
        bootstrap_nodes: Optional[List[KnownHost]] = None,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        continuous_mode: Optional[Dict[str, bool]] = None,
        network_names: Optional[List[str]] = None,
        print_discovered_peers: bool = True,
        dht: Optional[DHTConfig] = None,
    ):
        self.dht = dht or DHTConfig()
        self.bootstrap_nodes = bootstrap_nodes or self.dht.network.bootstrap_hosts
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

        # Reconcile constructor args with BitBootConfig values
        self._continuous_mode = continuous_mode or self._config.continuous_mode
        self._network_names = network_names or self._config.network_names
        self._network_objs = {
            name: NETWORK_REGISTRY.create(name) for name in self._network_names
        }
        self._discovered_peers: Dict[str, Dict[str, set]] = {
            name: {} for name in self._network_names
        }
        self._dht_manager = MultiDHTManager()
        self._dht_manager.add_network(
            self._config.dht.network, self._config.bootstrap_nodes
        )

    @classmethod
    async def create(cls,
                     config: Optional[BitBootConfig] = None,
                     continuous_mode: Optional[Dict[str, bool]] = None,
                     network_names: Optional[List[str]] = None
                     ) -> BitBoot:

        instance = cls(config, continuous_mode, network_names)
        instance._dht_manager.remove_network(instance._config.dht.network.name)
        await instance._dht_manager.add_network_async(
            instance._config.dht.network, instance._config.bootstrap_nodes
        )
        return instance

    def __del__(self):
        for manager in list(self._dht_manager._managers.values()):
            manager.stop()

    async def switch_dht_network(
        self,
        network: Union[str, DHTNetwork],
        bootstrap_nodes: Optional[List[KnownHost]] = None,
    ) -> None:
        """Switch the underlying DHT network BitBoot operates on."""

        self._dht_manager.remove_network(self._config.dht.network.name)
        await self._dht_manager.add_network_async(network, bootstrap_nodes)
        if isinstance(network, str):
            net = DHT_NETWORK_REGISTRY.get(network)
        else:
            net = network
        self._config.dht = DHTConfig(network=net, listen=self._config.dht.listen)
        self._config.bootstrap_nodes = bootstrap_nodes or net.bootstrap_hosts

    # -----------------------
    # Util
    # -----------------------
    async def lookup_and_announce(
        self,
        creator: Type[BitBoot],
        network_name: str,
        peer: KnownHost,
        peer_config: Optional[BitBootConfig] = None,
    ) -> None:
        """Announce a peer to a network and then perform a lookup.

        This helper is primarily used in examples where a peer first needs to
        make itself known and then query for other peers.

        Args:
            creator: The ``BitBoot`` instance acting as the network creator.
            network_name: Name of the network to interact with.
            peer: The peer address to announce.
            peer_config: Optional configuration for the announcing peer.
        """

        if peer_config is None:
            listening_host = creator._dht_manager.get_manager(
                creator._config.dht.network.name
            ).get_listening_host()
            peer_config = BitBootConfig(
                bootstrap_nodes=[listening_host],
                rate_limit_delay=1.0,
                max_retries=3,
                retry_delay=5.0,
            )
        self._config = peer_config
        await self.announce_peer(network_name, peer)
        await self.lookup(network_name)

    @staticmethod
    def load_network_names_from_file(filename: str) -> List[str]:
        with open(filename, "r") as f:
            return [line.strip() for line in f.readlines()]

    def _generate_info_hash(self, network_name: str) -> bytes:
        return hashlib.sha1(network_name.encode()).digest()

    def num_peers(self) -> Dict[str, int]:
        return {
            name: sum(len(p) for p in peers_by_dht.values())
            for name, peers_by_dht in self._discovered_peers.items()
        }

    # -----------------------
    # Lookup
    # -----------------------
    async def lookup(
        self,
        networks: Union[str, Network, List[Union[str, Network]]],
        num_searches: int = 10,
        delay: int = 5,
    ):
        if isinstance(networks, (str, Network)):
            networks = [networks]

        tasks = []
        for net in networks:
            if isinstance(net, str):
                network_obj = NETWORK_REGISTRY.get(net) or NETWORK_REGISTRY.create(net)
            else:
                network_obj = net
            for dht_net in network_obj.dht_networks:
                manager = self._dht_manager.get_manager(dht_net.name)
                if manager is None:
                    manager = self._dht_manager.add_network(dht_net)
                tasks.append(
                    self._lookup_single(
                        manager, network_obj.name, dht_net.name, num_searches, delay
                    )
                )

        await asyncio.gather(*tasks)

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry_error_callback=lambda _: logging.error("Failed to lookup network"))
    async def _lookup_single(
        self,
        manager: DHTManager,
        network_name: str,
        dht_network_name: str,
        num_searches: int,
        delay: int,
    ) -> None:
        info_hash = self._generate_info_hash(network_name)
        found_peers = set()

        for _ in range(num_searches):
            await asyncio.sleep(delay)
            results = await manager.get(info_hash)
            if results:
                for peer in results:
                    if isinstance(peer, tuple):
                        found_peers.add(peer)
                    elif isinstance(peer, str):
                        try:
                            host, port = peer.split(":")
                            found_peers.add((host, int(port)))
                        except ValueError:
                            continue

        peers_dict = self._discovered_peers.setdefault(network_name, {})
        peers_dict[dht_network_name] = found_peers

        union_peers = set().union(*peers_dict.values())

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f"{network_name}_peers.txt", "w") as f:
            for peer in union_peers:
                f.write(f"{peer}\n")
                if self._config.print_discovered_peers:
                    print(f"[{now}] {network_name}: {peer}")

    # -----------------------
    # Announce
    # -----------------------

    async def announce_peer(
        self,
        networks: Union[str, Network, List[Union[str, Network]]],
        peer: KnownHost,
    ):
        """Announce a peer address for one or more network names."""

        if isinstance(networks, (str, Network)):
            networks = [networks]

        tasks = []
        for net in networks:
            if isinstance(net, str):
                network_obj = NETWORK_REGISTRY.get(net) or NETWORK_REGISTRY.create(net)
            else:
                network_obj = net
            for dht_net in network_obj.dht_networks:
                manager = self._dht_manager.get_manager(dht_net.name)
                if manager is None:
                    manager = self._dht_manager.add_network(dht_net)
                tasks.append(
                    self._announce_peer_single(manager, network_obj.name, peer)
                )

        await asyncio.gather(*tasks)

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry_error_callback=lambda _: logging.error("Failed to announce peer"))
    async def _announce_peer_single(
        self, manager: DHTManager, network_name: str, peer: KnownHost
    ) -> None:
        """Announce a single peer address to the DHT."""

        info_hash = self._generate_info_hash(network_name)

        await manager.set(info_hash, f"{peer.host}:{peer.port}")

    # -----------------------
    # Continuous Mode
    # -----------------------
    async def start_continuous_mode(self, network_name: str):
        if network_name not in self._network_names:
            raise ValueError(
                f"Network name '{network_name}' is not configured")

        self._continuous_mode[network_name] = True
        while self._continuous_mode[network_name]:
            await self.lookup(network_name)
            await asyncio.sleep(self._config.rate_limit_delay)

    def stop_continuous_mode(self, network_name: str):
        self._continuous_mode[network_name] = False

    def continuous_mode_status(self) -> Dict[str, bool]:
        return self._continuous_mode
