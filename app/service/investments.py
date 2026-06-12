from typing import List, Tuple

from sqlalchemy import func

from app.models.charity_project import CharityProject
from app.models.donation import Donation


def investing_process(
    target_projects: List[CharityProject],
    target_donations: List[Donation]
) -> Tuple[List[CharityProject], List[Donation]]:
    """
    Распределяет средства от пожертвований в проекты.
    """
    sources_projects: List[CharityProject] = []
    sources_donations: List[Donation] = []

    # Основной цикл распределения средств
    for donation in target_donations:
        # Если пожертвование уже полностью распределено, пропускаем
        if donation.fully_invested:
            continue

        for project in target_projects:
            # Если проект уже закрыт, пропускаем
            if project.fully_invested:
                continue

            # Сколько еще нужно проекту?
            # Требуемая сумма - собранная на тек.момент сумма
            project_need = project.full_amount - project.invested_amount

            # Сколько еще осталось в пожертвовании?
            # Сумма пожертвования - сумма из пожертвования,
            # которая распределена по проектам
            donation_remains = donation.full_amount - donation.invested_amount

            if project_need <= 0 or donation_remains <= 0:
                continue

            # Определяем сумму трансфера (минимум из того,
            # что нужно и что есть)
            transfer_amount = min(project_need, donation_remains)

            # Обновляем значения в объектах (в памяти)
            project.invested_amount += transfer_amount
            donation.invested_amount += transfer_amount

            # Добавляем в списки изменённых объектов (если ещё не добавлены)
            if project not in sources_projects:
                sources_projects.append(project)
            if donation not in sources_donations:
                sources_donations.append(donation)

            # Проверяем, закрылся ли проект
            if project.invested_amount >= project.full_amount:
                project.fully_invested = True
                project.close_date = func.now()
            # Проверяем, полностью ли инвестировано пожертвование
            if donation.invested_amount >= donation.full_amount:
                donation.fully_invested = True
                donation.close_date = func.now()
                # Если деньги из этого пожертвования закончились,
                # выходим из цикла по проектам и переходим к следующему
                # пожертвованию
                break

    return sources_projects, sources_donations