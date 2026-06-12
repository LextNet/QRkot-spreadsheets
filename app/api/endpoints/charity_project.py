from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.api.validators import (
    check_name_duplicate, check_charity_project_exists,
    validate_project_deletion, validate_project_update
)


router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get('/',
            response_model=list[CharityProjectDB],
            response_model_exclude_none=True)
async def charity_project_get(session: SessionDep):
    """Для всех пользователей."""
    charity_projects = await charity_project_crud.get_multi(session)
    return charity_projects


@router.post('/',
             response_model=CharityProjectDB,
             dependencies=[Depends(current_superuser)],
             )
async def create_new_charity_project(
    charity_project: CharityProjectCreate,
    session: SessionDep
):
    """Для суперюзеров."""
    await check_name_duplicate(charity_project.name, session)
    new_charity_project = await charity_project_crud.create(charity_project,
                                                            session)
    return new_charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SessionDep,
):
    """Для суперюзеров."""
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    await validate_project_update(charity_project, obj_in)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
    project_id: int,
    session: SessionDep,
):
    """Для суперюзеров."""
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    await validate_project_deletion(charity_project)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project