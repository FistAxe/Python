import asyncio
from datetime import datetime

async def async_generator():
    for i in range(5):
        yield i
        await asyncio.sleep(1)  # Ensures the next value is scheduled after 1 second

async def main():
    async for value in async_generator():
        print(f'{datetime.now()}: {value}')

a = async_generator()

for _ in range(4):
    print(f"{asyncio.run(a.__anext__())}")

# Running the main coroutine
asyncio.run(main())