import os
import textwrap
from typing import Annotated

import google.generativeai as genai
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from IPython.display import Markdown

from app.data import models
from app.utils import GEMINI_API_KEY, get_current_active_user, get_dp


def to_markdown(text):
    text = text.replace("•", "  *")
    return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))


genai.configure(api_key=GEMINI_API_KEY)
gemini_pro_vision_model = genai.GenerativeModel(
    "gemini-pro",
    generation_config={"temperature": 0, "max_output_tokens": 400},
)


router_tag = "Gemi"

router = APIRouter(
    prefix="/chat-with-gemi",
    tags=[router_tag],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


async def sendQuestion(in_message: str):
    response = gemini_pro_vision_model.generate_content(in_message, stream=True)
    for chunk in response:
        yield (chunk.text)
        print(chunk.text)


@router.get("/gemi", tags=[router_tag])
async def sendMessage(
    message: str,
    # _: Annotated[models.User, Depends(get_current_active_user)]
):
    return StreamingResponse(
        sendQuestion(in_message=message),
        media_type="text/event-stream",
    )
