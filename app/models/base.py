from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, CommonMixin
from app.constants import (
    DEFAULT_FULL_AMOUNT, DEFAULT_INVEST_AMOUNT
)


class InvestmentBase(CommonMixin, Base):
    __abstract__ = True

    full_amount: Mapped[int] = mapped_column(Integer, nullable=False,
                                             default=DEFAULT_FULL_AMOUNT)
    invested_amount: Mapped[int] = mapped_column(Integer, nullable=False,
                                                 default=DEFAULT_INVEST_AMOUNT)
    fully_invested: Mapped[bool] = mapped_column(Boolean, default=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, nullable=False,
                                                  default=func.now())
    close_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint('full_amount > 0', name='check_full_amount_positive'),
        CheckConstraint('invested_amount <= full_amount',
                        name='check_invested_not_exceed_full'),
    )