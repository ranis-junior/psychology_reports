from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.auth.security import verify_password, create_access_token, CurrentUser
from app.models import User
from app.routers import Session
from app.schema.token import TokenSchema
from app.utils.rate_limit import login_rate_limiter

router = APIRouter(prefix="/auth", tags=["auth"], redirect_slashes=True)


@router.post('/token', response_model=TokenSchema)
async def request_access_token(request: Request, session: Session, form_data: OAuth2PasswordRequestForm = Depends()):
    client_ip = request.client.host if request.client else 'unknown'
    login_rate_limiter.check(client_ip)

    user_db: User | None = await session.scalar(select(User).where(User.username == form_data.username))
    if not user_db or not verify_password(form_data.password, user_db.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password.'
        )

    access_token = create_access_token(data={'sub': user_db.username})
    return TokenSchema(access_token=access_token, token_type='bearer')

@router.post('/refresh_token', response_model=TokenSchema)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(data={'sub': user.username})

    return TokenSchema(access_token=new_access_token, token_type='bearer')