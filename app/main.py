from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.core.init_db import create_first_superuser


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Всё, что указано выше yield, выполняется до запуска приложения.
    await create_first_superuser()

    # Lifespan-функция обязана вызывать yield,
    # но не должна возвращать никаких значений.
    yield
    # Все инструкции, описанные после yield,
    # выполняется перед завершением работы приложения.

app = FastAPI(title=settings.app_title,
              description=settings.description,
              lifespan=lifespan)

app.include_router(main_router)