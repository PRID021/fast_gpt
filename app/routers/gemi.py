import textwrap
from typing import Annotated

import google.generativeai as genai
from app.data import models
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from google.cloud import secretmanager
from IPython.display import Markdown
from app.utils import get_current_active_user, get_dp


def to_markdown(text):
    text = text.replace("•", "  *")
    return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))


project_id = "forward-deck-415709"
secret_id = "GOOGLE_API_KEY_ID"
parent = f"projects/{project_id}"
client = secretmanager.SecretManagerServiceClient()
name = "projects/187132938708/secrets/GOOGLE_API_KEY_ID/versions/1"
response = client.access_secret_version(request={"name": name})
payload = response.payload.data.decode("UTF-8")


genai.configure(api_key=payload)
gemini_pro_vision_model = genai.GenerativeModel("gemini-pro")


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
    message: str, _: Annotated[models.User, Depends(get_current_active_user)]
):
    return StreamingResponse(
        sendQuestion(in_message=message),
        media_type="text/event-stream",
    )
