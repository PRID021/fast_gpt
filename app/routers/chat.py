from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import render_text_description
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from ..data import crud, models, schemas
from ..data.database import get_session
from ..utils import OPENAI_API_KEY, get_current_active_user, get_dp
from .tools import create_account, delay, multiply, send_notification

llm = ChatOpenAI(
    temperature=0.9, model="gpt-3.5-turbo-0125", streaming=True, api_key=OPENAI_API_KEY
)

# Create prompt
# prompt = hub.pull("hwchase17/openai-tools-agent")


#  Retrieval step ingest .
embeddings_model = OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter()
loader = TextLoader("index.md")
docs = loader.load()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings_model)
retriever = vector.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "hoang_search",
    "Search for information about Hoang Pham. For any questions about Hoang, you must use this tool!",
)


tools = [retriever_tool, multiply, send_notification, delay, create_account]
llm_with_tools = llm.bind_tools(tools)
rendered_tools = render_text_description(tools)
system_prompt = f"""You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

{rendered_tools}

Given the user input, you have decide they asking for the tools or not.
If they asking for the tool, return your response as a JSON blob with 'name' and 'arguments' keys, if user missing some content ask them only for missing content.
If not response them appropriate.
"""
MEMORY_KEY = "chat_history"

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_prompt,
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Construct the OpenAI Tools agent
# agent = create_openai_tools_agent(llm, tools, prompt)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

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
        else:
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
