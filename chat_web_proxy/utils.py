from openai import OpenAI, AsyncOpenAI
import os
from pydantic import BaseModel
import asyncio

client = OpenAI(
     api_key=os.environ.get("OPENAI_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages= [
        {
            "role": "user",
            "content": "Say this is a test"
        }
    ],
    model="gpt-3.5-turbo",
)

async_client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

async def main():
    stream = await async_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "What population of vietname in 2021"}],
        stream=True,
    )
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run( main())