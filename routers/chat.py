from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from data import crud, models, schemas
from utils import async_client, get_current_active_user, get_dp

tags = ["Chat Service"]

router = APIRouter(
    prefix="/chat",
    tags=tags,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


async def sendQuestion(message: str, poster):
    stream = await async_client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": message}],
        stream=True,
    )
    content = ""
    async for chunk in stream:
        data = chunk.choices[0].delta.content or ""
        content += data
        yield (data)
    poster(content)


@router.get("/", tags=tags)
async def chat_stream(
    conversation_id: int,
    message: str,
    _: Annotated[models.User, Depends(get_current_active_user)],
):
    def poster(complete_message: str):
        db = get_dp()
        request_create_message = schemas.MessageCreate(content=complete_message)
        crud.create_conversation_message(
            db=db, conversation_id=conversation_id, message=request_create_message
        )

    return StreamingResponse(
        sendQuestion(message=message, poster=poster), media_type="text/event-stream"
    )


@router.post("/conversation", tags=tags, response_model=schemas.Conversation)
async def create_new_conversation(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_dp),
):
    request_create_conversation = schemas.ConversationCreate(title="")
    conversation = crud.create_user_conversation(
        db=db, conversation=request_create_conversation, user_id=current_user.id
    )
    return conversation


@router.get("/conversation", tags=tags, response_model=list[schemas.Conversation])
def get_user_conversations(
    current_active_user: Annotated[models.User, Depends(get_current_active_user)],
):
    return current_active_user.conversations
