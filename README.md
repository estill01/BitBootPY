# BitBootPy: Fully-Decentralized Peer Discovery For P2P Network Formation

###### Originally inspired by the BitBoot (Javascript) project: [https://github.com/tintfoundation/bitboot]()

`BitBootPy` is a Python library that enables fully-decentralized P2P network Peer Discovery and network formation. No centralized infrastructure is required to start or join a P2P network which uses `BitBootPy` for Peer Discovery. If you're tempted to use WebRTC for P2P network formation, you should be aware that WebRTC does require a centralized Peer Discovery server.


## Key Features
- **Piggybacks on the BitTorrent network** \
Makes a special entry on the BitTorrent DHT (distributed hash table) to enable robust decentralized peer discovery for your network without the need for centralized servers. As long as the BitTorrent network is running, your network will be discoverble. Can be extended to leverage other DHTs if necessary.

- **Self-Healing** \
Enables networks to easily re-form even if all nodes go offline.

- **Easy-to-use**\
A simple API for creating and joining decentralized networks

- **Async support**\
Supports both synchronous and asynchronous operation

## How it works
When you make a network using BitBoot / BitBootPy, you make an entry on the BitTorrent DHT with a unique key identifying your network. Anyone who wants to join your network then just has to search the BitTorrent DHT for that key, and then connect to your machine using the IP data contained in the DHT entry. Done and done. You now have a P2P network that is fully robust to all nodes going offline and does not require a central server for peer discovery.


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

For more examples and details on how to use BitBootPy, see the `examples` directory.

