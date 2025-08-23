import sys
import os
import asyncio
from bitbootpy import BitBoot, BitBootConfig


project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

async def main():
    print("Starting BitBoot..")
    # Create a network with the name "example_network"
    network_name = "example_network"

    # Initialize the BitBoot class for the creator of the network
    creator_config = BitBootConfig(
        bootstrap_nodes=None, rate_limit_delay=1.0, max_retries=3, retry_delay=5.0, continuous_mode=True
    )
    creator = await BitBoot.create(config=creator_config)

    while not creator._dht_manager.is_server_started():
        print("Waiting for server to start...")
        await asyncio.sleep(0.1)

    await creator._dht_manager.wait_for_server_start()

    print(f"Announcing network {network_name}..")
    await creator.announce_peer(network_names=[network_name], port=8000)

    # Simulate multiple peers joining the network
    peer_ports = [8001, 8002, 8003]

    listening_host = creator._dht_manager.get_listening_host()
    custom_peer_config = BitBootConfig(
        bootstrap_nodes=[listening_host],
        rate_limit_delay=1.0,
        max_retries=3,
        retry_delay=5.0,
    )

    peers = [BitBoot() for _ in range(len(peer_ports))]
    tasks = [
        peers[0].lookup_and_announce(creator, network_name, peer_ports[0], custom_peer_config),
        peers[1].lookup_and_announce(creator, network_name, peer_ports[1]),
        peers[2].lookup_and_announce(creator, network_name, peer_ports[2]),
    ]
    await asyncio.gather(*tasks)

    # Lookup for the joined peers from the creator's perspective
    await creator.lookup(network_names=[network_name])

    # Print the discovered peers for the example_network
    print("Discovered peers for the 'example_network':")
    print(creator._discovered_peers[network_name])

if __name__ == "__main__":
    asyncio.run(main())
