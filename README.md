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

## Built-in DHT networks and extensibility

BitBootPy ships with a small set of built-in DHT network definitions located in
`bitbootpy/core/dhtnetworks/`. Each module registers a ``DHTNetwork`` instance
when imported. The registry is populated automatically during startup, but you
can add your own networks by creating a similar module and ensuring it is
imported.

For local testing the package also provides a ``local`` network that has no
bootstrap hosts. Tests and examples can use this lightweight network without
reaching out to public DHT nodes.

### Using custom DHT backends

BitBootPy supports pluggable DHT backends.  The default implementation uses the
``kademlia`` library but alternative backends can be registered by inserting a
factory into :data:`bitbootpy.core.backends.BACKEND_REGISTRY`.  Each
``DHTNetwork`` specifies the backend it expects via the ``backend`` field.  See
``bitbootpy/examples/custom_backend.py`` for a minimal in-memory backend
demonstrating the registration process.

Most built-in network definitions (e.g. Ethereum or Solana) do not ship with
bootstrap host lists or working backends.  They act as placeholders so that
projects can supply the necessary dependencies and configuration at runtime.

## Blockchain backends

BitBootPy includes optional backends that persist DHT records directly on
popular blockchains.  Using these backends requires additional dependencies and
environment variables and will incur on-chain transaction fees whenever a value
is stored.  For development, always prefer running against testnets or local
nodes to avoid spending real funds and publishing data permanently.

### Bitcoin

- **Environment**: ``BITBOOTPY_BTC_KEY`` (WIF private key),
  ``BITBOOTPY_BTC_RPC_URL`` (JSON-RPC endpoint)
- **Dependency**: ``python-bitcoinlib``
- **Fees**: ``set`` writes an ``OP_RETURN`` transaction and pays the Bitcoin
  network fee.  Data is permanent and publicly visible.

### Ethereum

- **Environment**: ``BITBOOTPY_ETH_KEY`` (hex private key), ``BITBOOTPY_ETH_RPC``
  (RPC URL), ``BITBOOTPY_ETH_CONTRACT`` (storage contract address)
- **Dependencies**: ``web3`` and optional ``ddht`` for Discovery v5
- **Fees**: ``set`` submits a transaction to the contract and consumes gas.

### Solana

- **Environment**: ``BITBOOTPY_SOLANA_KEYPAIR`` (JSON or base58 keypair),
  optional ``BITBOOTPY_SOLANA_RPC`` (RPC URL)
- **Dependency**: ``solana``
- **Fees**: ``set`` creates or updates an account and pays lamports for rent
  and transaction fees.

### Arweave

- **Environment**: ``BITBOOTPY_ARWEAVE_WALLET`` (JWK wallet JSON), optional
  ``BITBOOTPY_ARWEAVE_GATEWAY`` (gateway URL)
- **Dependency**: ``arweave-python-client``
- **Fees**: ``set`` publishes a transaction requiring AR tokens.

**Warning**: Interacting with mainnet blockchains costs real cryptocurrency and
cannot be undone.  Use test networks such as Bitcoin ``regtest``/``testnet``,
Ethereum ``Sepolia``/``Goerli``, Solana ``devnet``, or the Arweave testnet
while developing.

