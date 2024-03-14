from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..data import crud, schemas
from ..utils import get_dp

router = APIRouter(
    prefix="/users",
    tags=["Authenticate"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.post("/register", tags=["Authenticate"], response_model=schemas.User)
def create_new_account(user: schemas.UserCreate, db: Session = Depends(get_dp)):
    db_user = crud.get_user_by_username(db=db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User name already registered.",
        )
    return crud.create_user(db=db, user=user)
