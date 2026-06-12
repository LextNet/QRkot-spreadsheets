from datetime import timedelta
from typing import Any

from sqlalchemy import asc, func, select
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
    ) -> list[dict[str, Any]]:
        closed_projects = await session.execute(
            select(
                CharityProject.name,
                CharityProject.description,
                (func.julianday(CharityProject.close_date) -
                 func.julianday(CharityProject.create_date)).label('duration'),
                CharityProject.create_date,
                CharityProject.close_date
            ).where(
                CharityProject.fully_invested,
                CharityProject.close_date.isnot(None)
            ).order_by(
                asc('duration')
            )
        )
        closed_projects = closed_projects.all()
        res = []
        for project in closed_projects:
            duration_seconds = int(project.duration * 86400)
            duration_timedelta = timedelta(seconds=duration_seconds)
            res.append({
                "name": project.name,
                "description": project.description,
                "duration": duration_timedelta
            })
        return res


donation_crud = CRUDDonation(Donation)
