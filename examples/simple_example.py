import asyncio
from bitboot import BitBoot, AsyncBitBoot

def synchronous_example():
    unique_key = 'your_unique_key_here'
    bitboot = BitBoot(unique_key)

    info_hash = bitboot.announce()
    found_peers = bitboot.lookup(info_hash)

    # Do something with the found peers
    print("All found peers:", found_peers)

    bitboot.stop()

async def asynchronous_example():
    unique_key = 'your_unique_key_here'
    bitboot = AsyncBitBoot(unique_key)

    info_hash = await bitboot.announce()
    found_peers = await bitboot.lookup(info_hash)

    # Do something with the found peers
    print("All found peers:", found_peers)

    bitboot.stop()

if __name__ == "__main__":
    print("Running synchronous example...")
    synchronous_example()

    print("\nRunning asynchronous example...")
    asyncio.run(asynchronous_example())

