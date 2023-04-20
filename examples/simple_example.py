import asyncio
from bitboot import BitBoot, AsyncBitBoot

def synchronous_example():
    unique_key = 'your_unique_key_here'
    bitboot = BitBoot(unique_key)

    info_hash = bitboot.announce()
    found_peers = bitboot.lookup(info_hash)

    # Do something with the found peers
    print("All found peers:", found_peers)

