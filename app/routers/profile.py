from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from ..data import crud, models, schemas
from ..utils import get_current_active_user, get_dp

router = APIRouter(
    prefix="/user",
    tags=["Profile"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/me", tags=["Profile"], response_model=schemas.UserResponse)
async def read_users_me(
    current_users: Annotated[models.User, Depends(get_current_active_user)]
):
    return current_users


@router.post(
    "/me/uploadfile/",
    # response_model=schemas.UploadAvatar,
    description="Upload image file for user avatar",
    summary="Use to upload user avatar",
)
async def create_upload_file(
    file: Annotated[UploadFile, File(description="User avatar")],
    current_users: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_dp),
):
    contents = await file.read()
    create_upload_avatar = schemas.CreateUploadAvatar(
        filename=file.filename, contents=contents, user_id=current_users.id
    )
    file_upload = crud.upload_file(db=db, file=create_upload_avatar)
    return file_upload.owner_id


@router.get("/me/items")
async def read_own_items(
    current_user: Annotated[models.User, Depends(get_current_active_user)]
):
    return [{"items": "Foo", "owner": current_user.username}]
