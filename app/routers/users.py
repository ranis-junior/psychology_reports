from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from app.auth.security import get_password_hash, CurrentUser, create_verification_token, get_current_user
from app.models.user import User
from app.routers import Session
from app.schema.user import UserInsertSchema, UserSchema, UserUpdateSchema
from app.settings import settings
from app.tasks.email import send_verification_email

router = APIRouter(prefix="/users", tags=["users"], redirect_slashes=True, dependencies=[Depends(get_current_user)])


@router.get("/{id_user}", response_model=UserSchema)
async def find_by_id(id_user: int, session: Session):
    db_user = await session.scalar(
        select(User).where(User.id == id_user).options(joinedload(User.psychologist))
    )
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    return UserSchema.model_validate(db_user)


@router.put('/{id_user}', response_model=UserSchema)
async def update_user(
        id_user: int,
        user: UserUpdateSchema,
        session: Session
):
    db_user: User | None = await session.scalar(
        select(User).where(User.id == id_user)
    )

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    db_user.username = user.username if user.username is not None else db_user.username
    db_user.active = user.active if user.active is not None else db_user.active
    if user.password:
        db_user.password = get_password_hash(user.password)
    db_user.email = user.email if user.email is not None else db_user.email

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.delete('/{id_user}', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
        id_user: int,
        session: Session
):
    db_user = await session.scalar(
        select(User).where(User.id == id_user)
    )

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    await session.delete(db_user)
    await session.commit()
