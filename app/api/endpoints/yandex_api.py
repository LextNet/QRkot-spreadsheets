from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.yandex_client import get_yandex_client, YandexDiskClient
from app.core.user import current_superuser
from app.crud.donation import donation_crud
from app.service.yandex_api import (
    set_user_permissions,
    create_simple_report,
    update_simple_report
)

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
    summary="Создать Excel-отчёт на Яндекс Диске",
    description="""
    Создаёт Excel-файл с отчётом по инвестированию в проекты.
    Файл сохраняется на Яндекс Диске в папке "Reports"
    и становится доступен по публичной ссылке.

    Требуются права суперпользователя.
    """
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        yandex_client: YandexDiskClient = Depends(get_yandex_client)
) -> str:
    """
    Создание отчёта в Excel-файле на Яндекс Диске
    """
    closed_projects = await donation_crud.get_projects_by_completion_rate(
        session=session
    )
    if not closed_projects:
        raise HTTPException(
            status_code=404,
            detail="Нет данных для формирования отчёта"
        )
    try:
        # Создаём файл и получаем ссылку для загрузки
        upload_url, file_path = await create_simple_report(yandex_client)
        # Записываем данные в Excel
        await update_simple_report(upload_url, closed_projects, yandex_client)
        # Делаем файл публичным и получаем ссылку
        public_url = await set_user_permissions(file_path, yandex_client)

        return public_url

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании отчёта: {str(e)}"
        )