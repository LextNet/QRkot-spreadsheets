import io
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import Row
import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient


def format_time_delta(time_left: timedelta):
    days = time_left.days
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    if days > 0:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
        yandex_client: YandexDiskClient,
        folder: str = "Reports"
) -> tuple[str, str]:
    """Создаёт Excel-файл и возвращает upload_url и file_path"""
    now_date_time = datetime.now().strftime(settings.report_format)
    safe_filename = f"Отчет_{now_date_time}".replace(
        ':', '-').replace(' ', '_').replace('/', '-')
    upload_url, file_path = await yandex_client.create_excel_file(
        safe_filename, folder)
    return upload_url, file_path


async def update_simple_report(
        upload_url: str,
        closed_projects: List[Row],
        yandex_client: YandexDiskClient
) -> None:
    """Записывает данные в Excel-файл и загружает на Яндекс Диск"""
    now_date_time = datetime.now().strftime(settings.report_format)
    # Создаём Excel-файл в памяти
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Отчет")
    # Форматы
    title_format = workbook.add_format({'bold': True, 'font_size': 14})
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2F75B5',
        'font_color': 'white',
        'border': 1,
        'align': 'center'
    })
    cell_format = workbook.add_format({'border': 1, 'align': 'center'})
    count_row_format = workbook.add_format({'bold': True})
    # Заголовок отчёта
    worksheet.merge_range('A1:C1', f"Отчет от {now_date_time}", title_format)
    # Заголовки колонок
    headers = ['Название проекта', 'Время сбора', 'Описание']
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)
    # Данные
    for row, res in enumerate(closed_projects, start=2):
        format_duration = format_time_delta(timedelta(seconds=int(
            res.duration * 86400)))
        worksheet.write(row, 0, str(res.name), cell_format)
        worksheet.write(row, 1, str(format_duration), cell_format)
        worksheet.write(row, 2, str(res.description), cell_format)
    count_row = len(closed_projects)
    worksheet.merge_range(f'A{count_row + 3}:C{count_row + 3}',
                          f'Всего проектов: {str(count_row)}',
                          count_row_format)
    # Настраиваем ширину колонок
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 10)
    worksheet.set_column('C:C', 25)

    workbook.close()
    output.seek(0)

    # Загружаем файл на Яндекс Диск
    await yandex_client.upload_file(upload_url, output.getvalue())


async def set_user_permissions(
        file_path: str,
        yandex_client: YandexDiskClient
) -> str:
    """Делает файл публичным и возвращает ссылку"""
    return await yandex_client.publish_file(file_path)
