from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from utils import async_client, get_current_active_user

router = APIRouter(
    prefix="/chat",
    tags=["Chat Service"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


async def sendQuestion(message: str):
    stream = await async_client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": message}],
        stream=True,
    )
    async for chunk in stream:
        yield (chunk.choices[0].delta.content or "")


@router.get("", tags=["Chat Service"])
async def chat_stream(
    message: str, token: Annotated[str, Depends(get_current_active_user)]
):
    return StreamingResponse(
        sendQuestion(message=message), media_type="text/event-stream"
    )
