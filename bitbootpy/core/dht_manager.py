from __future__ import annotations
from typing import List, Tuple, Set
from kademlia.network import Server
from kademlia.routing import KBucket
import asyncio


KNOWN_HOSTS: Dict[str, List[Set[str, int]]]  = {
        "bit_torrent": [
            ("dht.transmissionbt.com", 6881),
            ("dht.u-phoria.org", 6881),
            ("dht.bt.am", 2710),
            ("dht.ipred.org", 6969),
            ("dht.pirateparty.gr", 80),
            ("dht.zoink.nl", 80),
            ("dht.openbittorrent.com", 80),
            ("dht.istole.it", 6969),
            ("dht.ccc.de", 80),
            ("dht.leechers-paradise.org", 6969)
        ],
        "btc": [(),(),],
        "sol": [(),()],
        "eth": [(),()],
        "ipfs": [(),()],
        "arweave": [(),()]
}


class DHTManager:
    def __init__(self, bootstrap_nodes: List[Tuple[str, int]] = BT_DHT_DOMAINS):
        self._server = Server()
        self._bootstrap_nodes = bootstrap_nodes

    @classmethod
    async def create(cls, bootstrap_nodes: List[Tuple[str, int]] = None):
        print("DHTManager.create()")
        instance = cls(bootstrap_nodes)
        await instance._bootstrap_dht()
        return instance

    async def _bootstrap_dht(self, port: int = 5678):
        print("DHTManager._bootstrap_dht()")
        await self._server.listen(port)

        # Connect to known nodes
        for node in self._bootstrap_nodes:
            print("DHTManager._bootstrap_dht(): node = ", node)
            await self._server.bootstrap([node])

    def get_routing_table(self) -> List[KBucket]:
        return self._server.protocol.router.buckets

    def is_server_started(self) -> bool:
        return bool(self._server.transport)

    async def wait_for_server_start(self):
        while not self._server.transport:
            await asyncio.sleep(0.1)

    def stop(self):
        self._server.stop()

    def get_server(self):
        return self._server
