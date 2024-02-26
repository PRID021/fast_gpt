from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from data import crud, models, schemas
from data.database import get_session
from utils import  get_current_active_user, get_dp

llm = ChatOpenAI(temperature=0.9)

prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ]
)

tags = ["Chat Service"]

router = APIRouter(
    prefix="/chat",
    tags=tags,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


async def sendQuestion(user: models.User, in_message: str, poster):
    chat_history = []
    for message in user.conversations[-1].messages:
        if message.sender == schemas.Sender.HU:
            chat_history.append(HumanMessage(content=message.content))
        else:
            chat_history.append(AIMessage(content=message.content))
    history_chain = prompt | llm
    
    for m in chat_history:
        print(m.content)
    content = ""
    for chunk in history_chain.stream(
        {"chat_history": chat_history, "input": in_message}
    ):
        data = chunk.content
        content += data
        yield data
    
    poster(complete_message = in_message,sender = schemas.Sender.HU)
    poster(complete_message = content, sender = schemas.Sender.AI)
    

@router.get("", tags=tags)
async def chat_stream(
    conversation_id: int,
    message: str,
    user: Annotated[models.User, Depends(get_current_active_user)],
):
    def poster(complete_message: str, sender: schemas.Sender):
        db = get_session()
        request_create_message = schemas.MessageCreate(
            content=complete_message, sender=sender, id=None
        )
        crud.create_conversation_message(
            db=db, conversation_id=conversation_id, message=request_create_message
        )

    return StreamingResponse(
        sendQuestion(user=user, message=message, poster=poster),
        media_type="text/event-stream",
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
