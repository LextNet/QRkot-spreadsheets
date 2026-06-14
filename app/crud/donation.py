from typing import List

from sqlalchemy import asc, func, Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject, Donation, User


class CRUDDonation(CRUDBase):
    async def get_by_user(
            self,
            user: User,
            session: AsyncSession
    ):
        donations = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        return donations.scalars().all()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ) -> List[Row]:
        closed_projects = await session.execute(
            select(
                CharityProject.name,
                CharityProject.description,
                (func.julianday(CharityProject.close_date) -
                 func.julianday(CharityProject.create_date)).label('duration')
            ).where(
                CharityProject.fully_invested,
                CharityProject.close_date.isnot(None)
            ).order_by(
                asc('duration')
            )
        )
        closed_projects = closed_projects.all()
        return closed_projects


donation_crud = CRUDDonation(Donation)
