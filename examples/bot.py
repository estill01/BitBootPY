from bitboot.async_bitboot import AsyncBitBoot
import httpx
import uuid


# TODO Review / fix
class Bot:
    def __init__(self, shared_unique_key, bootstrap_nodes=None):
        self.unique_key = uuid.uuid4().hex
        self.async_bitboot = AsyncBitBoot(shared_unique_key, bootstrap_nodes)

    async def join_network(self):
        self.info_hash = await self.async_bitboot.announce()
        self.found_peers = await self.async_bitboot.lookup(self.info_hash)
        print(f"Bot {self.unique_key} found peers:", self.found_peers)

    async def exchange_messages(self, message):
        if len(self.found_peers) == 0:
            print(f"Bot {self.unique_key} has no peers to exchange messages with.")
            return

        peer = list(self.found_peers)[0]
        async with aiohttp.ClientSession() as session:
            url = f"http://{peer[0]}:{peer[1]}/message"
            async with session.post(url, data=message.encode()) as response:
                response_text = await response.text()
                print(f"Bot {self.unique_key} received response: {response_text}")

    def stop(self):
        self.async_bitboot.stop()



