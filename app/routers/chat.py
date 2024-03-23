from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from ..data import crud, models, schemas
from ..data.database import get_session
from ..utils import OPENAI_API_KEY, get_current_active_user, get_dp
from .tools import delay, multiply, send_notification

llm = ChatOpenAI(
    temperature=0.9, model="gpt-3.5-turbo-0125", streaming=True, api_key=OPENAI_API_KEY
)
prompt = hub.pull("hwchase17/openai-tools-agent")

# prompt =  (
#     ChatPromptTemplate.from_messages(
#         [
#             MessagesPlaceholder(variable_name="chat_history"),
#             ("user", "{input}"),
#         ]
#     )

# )


tools = [multiply, send_notification, delay]
# Construct the OpenAI Tools agent
agent = create_openai_tools_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, return_intermediate_steps=True
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
            # print(f"from chat history with role HU: {message.content}")
        else:
            # print(f"from chat history with role AI: {message.content}")
            chat_history.append(AIMessage(content=message.content))

    content = ""
    async for event in agent_executor.astream_events(
        {"chat_history": chat_history, "input": f"{in_message}"}, version="v1"
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            data = event["data"]["chunk"].content
            if data:
                content += data
                yield data

    poster(complete_message=in_message, sender=schemas.Sender.HU)
    poster(complete_message=content, sender=schemas.Sender.AI)


@router.get("", tags=tags)
async def chat_stream(
    conversation_id: int,
    message: str,
    user: Annotated[models.User, Depends(get_current_active_user)],
):
    def check_message():
        user_conversations: list[models.Conversation] = user.conversations
        for conversation in user_conversations:
            if conversation.id == conversation_id:
                return True
        return False

    def poster(complete_message: str, sender: schemas.Sender):
        db = get_session()
        request_create_message = schemas.MessageCreate(
            sender=sender,
            content=complete_message,
        )
        created_message = crud.create_conversation_message(
            db=db,
            message=request_create_message,
            conversation_id=conversation_id,
        )

    if not check_message():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found conversation",
        )

    return StreamingResponse(
        sendQuestion(user=user, in_message=message, poster=poster),
        media_type="text/event-stream",
    )


@router.post("/conversation", tags=tags, response_model=schemas.ConversationResponse)
async def create_new_conversation(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_dp),
):
    request_create_conversation = schemas.ConversationCreate(title="")
    conversation = crud.create_user_conversation(
        db=db, conversation=request_create_conversation, user_id=current_user.id
    )
    return conversation


@router.get(
    "/conversation", tags=tags, response_model=list[schemas.ConversationResponse]
)
def get_user_conversations(
    current_active_user: Annotated[models.User, Depends(get_current_active_user)],
):
    return current_active_user.conversations


@router.get(
    "/conversation/{conversation_id}",
    tags=tags,
    # , response_model=list[schemas.Message]
)
def get_conversation_messages(
    conversation_id,
    current_active_user: Annotated[models.User, Depends(get_current_active_user)],
):
    user_conversations: List[models.Conversation] = current_active_user.conversations
    for conversation in user_conversations:
        if conversation.id == int(conversation_id):
            return conversation.messages
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Can't found conversation"
    )
