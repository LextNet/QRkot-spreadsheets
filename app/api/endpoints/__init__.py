from app.api.endpoints.charity_project import router as charity_project_router
from app.api.endpoints.donation import router as donation_router
from app.api.endpoints.user import router as user_router
from app.api.endpoints.yandex_api import router as yandex_router


__all__ = [
    "charity_project_router",
    "donation_router",
    "user_router",
    "yandex_router"
]