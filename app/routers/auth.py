from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.auth.security import verify_password, create_access_token, CurrentUser
from app.models import User
from app.routers import Session
from app.schema.token import TokenSchema

router = APIRouter(prefix="/auth", tags=["auth"], redirect_slashes=True)


@router.post('/token', response_model=TokenSchema)
async def request_access_token(session: Session, form_data: OAuth2PasswordRequestForm = Depends()):
    user_db: User | None = await session.scalar(select(User).where(User.email == form_data.username))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email.'
        )

    if not verify_password(form_data.password, user_db.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect password.'
        )

    access_token = create_access_token(data={'sub': user_db.username})
    return TokenSchema(access_token=access_token, token_type='bearer')

@router.post('/refresh_token', response_model=TokenSchema)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(data={'sub': user.username})

    return {'access_token': new_access_token, 'token_type': 'bearer'}