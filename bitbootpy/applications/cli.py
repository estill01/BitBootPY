"""Command line interface for BitBootPY."""

from __future__ import annotations

import argparse
import json
import sys
from asyncio import gather, run
from typing import List

from bitbootpy import BitBoot, BitBootConfig, KnownHost


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
        "--peer-host",
        default="127.0.0.1",
        help="Host address of the peer to announce (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--peer-port",
        type=int,
        default=6881,
        help="Port number of the peer to announce (default: 6881)",
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
        with open(args.config, "r") as f:
            loaded_config = json.load(f)
        config = BitBootConfig(**loaded_config)

    if args.network_names_file:
        config.load_network_names_from_file(args.network_names_file)

    bitboot = await BitBoot.create(config=config)

    tasks = []
    if args.announce:
        peer = KnownHost(args.peer_host, args.peer_port)
        for network_name in args.announce:
            tasks.append(bitboot.announce_peer(network_name, peer))
    if args.lookup:
        for network_name in args.lookup:
            tasks.append(bitboot.lookup(network_name))
    if args.continuous:
        for network_name in args.continuous:
            tasks.append(bitboot.start_continuous_mode(network_name))

    if tasks:
        await gather(*tasks)
    else:
        parser.print_help()


if __name__ == "__main__":
    run(main(sys.argv[1:]))

