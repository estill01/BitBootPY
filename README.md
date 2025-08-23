# BitBootPy: Fully-Decentralized Peer Discovery For P2P Network Formation

###### Originally inspired by the BitBoot (Javascript) project: [https://github.com/tintfoundation/bitboot]()

`BitBootPy` is a Python library that enables fully-decentralized P2P network Peer Discovery and network formation. No centralized infrastructure is required to start or join a P2P network which uses `BitBootPy` for Peer Discovery. If you're tempted to use WebRTC for P2P network formation, you should be aware that WebRTC does require a centralized Peer Discovery server.


## Key Features
- **Leverages existing DHT networks** \
Creates a special entry on your chosen DHT (e.g., BitTorrent) to enable robust decentralized peer discovery for your network without the need for centralized servers. As long as that DHT network is running, your network will be discoverable.

- **Self-Healing** \
Enables networks to easily re-form even if all nodes go offline.

- **Easy-to-use**\
A simple API for creating and joining decentralized networks

- **Async-first design**\
Built on ``asyncio`` for high concurrency.

- **Multi-network support**\
Switch between different DHT networks or register your own at runtime using helper utilities.

- **Command-line interface**\
Announce or look up peers from the terminal and optionally poll continuously for new peers.

## How it works
When you make a network using BitBoot / BitBootPy, you make an entry on the selected DHT (such as the BitTorrent DHT) with a unique key identifying your network. Anyone who wants to join then searches that DHT for the key and connects to your machine using the IP data contained in the entry. Done and done. You now have a P2P network that is fully robust to all nodes going offline and does not require a central server for peer discovery.


## Usage
To use BitBootPy, create a :class:`BitBoot` instance and announce a
:class:`KnownHost` before looking up peers. Here's a simple example:

```python
import asyncio
from bitbootpy import BitBoot, BitBootConfig, KnownHost

async def main():
    bitboot = await BitBoot.create(BitBootConfig())
    await bitboot.announce_peer("unique_network", KnownHost("127.0.0.1", 6881))
    await bitboot.lookup("unique_network")

if __name__ == "__main__":
    asyncio.run(main())
```

For more examples and details on how to use BitBootPy, see the `bitbootpy/examples` directory.

## Command-line interface
Run the CLI to announce or discover peers without writing code:

```bash
python -m bitbootpy.applications.cli --announce mynet --peer-host 127.0.0.1 --peer-port 6881
python -m bitbootpy.applications.cli --lookup mynet
```

Use ``--continuous mynet`` to poll for peers continuously or ``--help`` for all options.

