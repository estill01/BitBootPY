# BitBootPY - Fully-Decentralized Peer Discovery For P2P Networks

# Want to start a decentralized network, but don't know any peer IDs?
# No sweat! BitBootPY has your back.
from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Union, Type, TYPE_CHECKING
import hashlib
import datetime
import json
from kademlia.network import Server

# from twisted.internet import reactor, defer, asyncioreactor
# from twisted.names import client

import asyncio

from tenacity import retry, wait_fixed, stop_after_attempt
import logging
import argparse
import sys

BT_DHT_DOMAINS = [
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
]


# Managest connection to the BitTorrent network so the main BitBoot class can function
class DHTManager:
    def __init__(self, bootstrap_nodes: List[Tuple[str, int]] = BT_DHT_DOMAINS ):
        self._server = Server()
        self._bootstrap_nodes = bootstrap_nodes 

    @classmethod
    async def create(cls, bootstrap_nodes: List[Tuple[str, int]] = None):
        print("DHTManager.create()")
        instance = cls(bootstrap_nodes)
        yield instance._bootstrap_dht()
        return instance

    async def _bootstrap_dht(self):
        print("DHTManager._bootstrap_dht()")

        # need to call(?):
        # await self._server.listen(5678) # or some other port

        async def resolve_and_bootstrap(node):
            host, port = node

            # get IP addresses; got it... ; TODO swap this code out
            ip = await client.getHostByName(host)

            print("DHTManager._bootstrap_dht(): ip = ", ip)
            yield self._server.bootstrap([(ip, port)])

        for node in self._bootstrap_nodes:
            print("DHTManager._bootstrap_dht(): node = ", node)
            await resolve_and_bootstrap(node)
            # reactor.callLater(0, resolve_and_bootstrap, node)

    def is_server_started(self) -> bool:
        return bool(self._server.transport)

    async def wait_for_server_start(self):
        while not self._server.transport:
            await asyncio.sleep(0.1)


    def stop(self):
        self._server.stop()

    def get_server(self):
        return self._server
