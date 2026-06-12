from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from app.constants import (
    MIN_FULL_AMOUNT, DEFAULT_INVEST_AMOUNT, MIN_INVEST_AMOUNT
)


class InvestmentBase(BaseModel):
    full_amount: int = Field(gt=MIN_FULL_AMOUNT)
    invested_amount: int = Field(default=DEFAULT_INVEST_AMOUNT,
                                 ge=MIN_INVEST_AMOUNT)
    fully_invested: bool = Field(default=False)
    create_date: datetime
    close_date: Optional[datetime] = None

    @field_serializer('close_date')
    def serialize_close_date(self, close_date: Optional[datetime]) -> str:
        return close_date.isoformat() if close_date else ""
