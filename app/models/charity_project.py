from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import MAX_LENGTH_NAME_PROJECT
from app.models.base import InvestmentBase


class CharityProject(InvestmentBase):
    name: Mapped[str] = mapped_column(String(MAX_LENGTH_NAME_PROJECT),
                                      unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)