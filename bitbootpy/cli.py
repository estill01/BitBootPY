# BitBootPY - Fully-Decentralized Peer Discovery For P2P Networks

from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Union, Type, TYPE_CHECKING
import hashlib
import datetime
import json
from kademlia.network import Server
# from twisted.internet import reactor, defer, asyncioreactor
# from twisted.names import client
from tenacity import retry, wait_fixed, stop_after_attempt
import logging
import argparse
from asyncio import gather, create_task, run
import sys

from bitbootpy.bitbootpy import BitBoot 


async def main(argv: List[str]):
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
    parser.add_argument(
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

    async with BitBoot.create(config=config) as bitboot:

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
                await gather(*tasks)

        if args.announce or args.lookup or args.continuous:
            create_task(run_async_tasks())
        else:
            parser.print_help()
    
if __name__ == "__main__":
    run(main(sys.argv[1:]))
