import asyncio
import bitbootpy

bitboot = BitBoot()
network_names = ["network1", "network2"]

async def main_async():
    await bitboot.start_continuous_mode(network_names)

# Start the continuous mode in the background
loop = asyncio.get_event_loop()
task = loop.create_task(main_async())

# Stop the continuous mode after 60 seconds
time.sleep(60)
bitboot.stop_continuous_mode()

# Wait for the continuous mode task to finish
loop.run_until_complete(task)

