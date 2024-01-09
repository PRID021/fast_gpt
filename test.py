import json
from datetime import datetime

import aiohttp
import asyncio

import requests

url = 'http://127.0.0.1:8000/chat'

async def get_json_events():
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            while True:
                chunk = await resp.content.readline()
                if not chunk:
                    break
                yield json.loads(chunk.decode("utf-8"))
async def main():
    async for event in get_json_events():
        print(event)

asyncio.run(main=main())