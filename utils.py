from openai import OpenAI, AsyncOpenAI
import os


client = OpenAI(
     api_key=os.environ.get("OPENAI_API_KEY"),
)

async_client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

async def sendQuestion(message: str):
    stream = await async_client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": message}],
        stream=True,
    )
    async for chunk in stream:
        yield (chunk.choices[0].delta.content or "")