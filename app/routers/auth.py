from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select, or_

from app.auth.security import verify_password, create_access_token, CurrentUser, \
    create_verification_token, decode_verification_token, get_password_hash
from app.models import User, Psychologist
from app.routers import Session
from app.schema.token import TokenSchema
from app.schema.user import ResendVerificationSchema, VerifyEmailSchema, UserSchema, UserInsertSchema
from app.settings import settings
from app.tasks.email import send_verification_email
from app.utils.rate_limit import login_rate_limiter, verification_rate_limiter

router = APIRouter(prefix="/auth", tags=["auth"], redirect_slashes=True)


@router.post('/register/user', status_code=HTTPStatus.CREATED, response_model=UserSchema)
async def register_new_user(user: UserInsertSchema, session: Session):
    db_user = await session.scalar(
        select(User).where(
            or_(User.username == user.username, User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.'
        )

    db_user_insert = User(
        active=False,
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )

    session.add(db_user_insert)
    await session.flush()

    if user.psychologist is not None:
        db_psychologist_insert= Psychologist(
            user.psychologist.name,
            birth_date=user.psychologist.birth_date,
            crp=user.psychologist.crp,
            id_user=db_user_insert.id
        )
        session.add(db_psychologist_insert)

    await session.commit()
    await db_user_insert.awaitable_attrs.psychologist

    verification_token = create_verification_token(db_user_insert)
    await send_verification_email.kiq(
        db_user_insert.email,
        verification_token,
        settings.VERIFICATION_TOKEN_EXPIRE_MINUTES,
    )

    return db_user_insert


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
    await user_db.awaitable_attrs.psychologist
    if not user_db.active:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Account not verified. Please validate your email first.'
        )

    access_token = create_access_token(data={'sub': user_db.username})
    return TokenSchema(access_token=access_token, token_type='bearer', user=UserSchema.model_validate(user_db))


@router.post('/refresh_token', response_model=TokenSchema)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(data={'sub': user.username})

    return TokenSchema(access_token=new_access_token, token_type='bearer', user=UserSchema.model_validate(user))


@router.post('/verify/email/send', status_code=HTTPStatus.ACCEPTED)
async def send_verification_email_endpoint(
        request: Request,
        payload: ResendVerificationSchema,
        session: Session,
):
    client_ip = request.client.host if request.client else 'unknown'
    verification_rate_limiter.check(f'{client_ip}:{payload.email}')

    db_user: User | None = await session.scalar(
        select(User).where(User.email == payload.email)
    )

    if db_user and not db_user.active:
        token = create_verification_token(db_user)
        await send_verification_email.kiq(
            db_user.email,
            token,
            settings.VERIFICATION_TOKEN_EXPIRE_MINUTES,
        )

    return {'message': 'If the email is registered, a verification link has been sent.'}


@router.post('/verify/email', status_code=HTTPStatus.OK)
async def verify_email(payload: VerifyEmailSchema, session: Session):
    try:
        data = decode_verification_token(payload.token)
    except (DecodeError, ExpiredSignatureError, InvalidTokenError):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid or expired verification token.'
        )

    if data.get('type') != 'email_verification':
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid verification token.'
        )

    try:
        user_id = int(data['sub'])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid verification token.'
        )

    db_user: User | None = await session.scalar(
        select(User).where(User.id == user_id)
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found.'
        )

    if db_user.active:
        return {'message': 'Account already verified.'}

    db_user.active = True
    session.add(db_user)
    await session.commit()

    return {'message': 'Account verified successfully.'}
