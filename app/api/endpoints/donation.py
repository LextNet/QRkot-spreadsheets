from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.donation import donation_crud
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.core.user import current_user, current_superuser
from app.models import User


router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get('/',
            response_model=list[DonationFullInfoDB],
            response_model_exclude_none=True)
async def donation_get(
    session: SessionDep,
    user: Annotated[User, Depends(current_superuser)]
):
    """Для суперюзеров."""
    donations = await donation_crud.get_multi(session)
    return donations


@router.post('/',
             response_model=DonationDB,
             response_model_exclude_none=True)
async def donation_post(
        donation: DonationCreate,
        session: SessionDep,
        user: Annotated[User, Depends(current_user)]
):
    """Для зарегистрированного пользователя."""
    new_donation = await donation_crud.create(
        donation, session, user
    )
    return new_donation


@router.get(
    '/my',
    response_model=list[DonationDB],
)
async def get_my_donations(
        session: SessionDep,
        user: Annotated[User, Depends(current_user)]
):
    """Получает список всех пожертвований для текущего пользователя."""
    donations = await donation_crud.get_by_user(
        session=session, user=user
    )
    return donations