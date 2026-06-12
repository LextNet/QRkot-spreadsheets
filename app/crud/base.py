from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, select, false, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation, User
from app.service.investments import investing_process


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
        user: Optional[User] = None
    ):
        obj_in_data = obj_in.model_dump()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        db_obj.create_date = datetime.utcnow()
        session.add(db_obj)

        # Сохраняем объект в БД, чтобы он получил ID и стал доступен для
        # других запросов
        await session.flush()
        target_projects = await self._get_open_sources(CharityProject, session)
        target_donations = await self._get_open_sources(Donation, session)

        # Получаем изменённые объекты
        sources_projects, sources_donations = investing_process(
            target_projects,
            target_donations)

        # Добавляем все изменённые объекты в сессию
        for project in sources_projects:
            session.add(project)
        for donation in sources_donations:
            session.add(donation)

        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        # Проверка после обновления
        if db_obj.invested_amount >= db_obj.full_amount:
            db_obj.fully_invested = True
            db_obj.close_date = func.now()
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def _get_open_sources(
            self,
            db_obj,
            session: AsyncSession
    ):
        sources = select(db_obj).where(
            and_(
                db_obj.fully_invested == false(),
                db_obj.full_amount > db_obj.invested_amount
            )
        ).order_by(db_obj.create_date)

        result = await session.execute(sources)
        return result.scalars().all()