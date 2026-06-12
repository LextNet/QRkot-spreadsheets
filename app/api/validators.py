from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject
from app.schemas.charity_project import CharityProjectUpdate


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return charity_project


async def validate_project_deletion(
        project: CharityProject
) -> None:
    # нельзя удалить закрытый проект
    if project.fully_invested or project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='Cannot delete fully_invested project'
        )


async def validate_project_update(
        project: CharityProject,
        project_update: CharityProjectUpdate
) -> None:
    # нельзя редактировать закрытый проект
    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit a fully invested (closed) project"
        )
    update_data = project_update.model_dump(exclude_unset=True)
    new_full_amount = update_data.get('full_amount')
    if new_full_amount is not None:
        if new_full_amount < project.invested_amount:
            raise HTTPException(
                status_code=400,
                detail=f'Cannot set full_amount ({new_full_amount}) '
                       f'less than invested_amount ({project.invested_amount})'
            )
