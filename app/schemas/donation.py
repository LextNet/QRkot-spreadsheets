from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.constants import MIN_FULL_AMOUNT
from app.schemas.base import InvestmentBase


class DonationCreate(BaseModel):
    full_amount: int = Field(gt=MIN_FULL_AMOUNT)
    comment: Optional[str] = None


class DonationDB(BaseModel):
    id: int
    full_amount: int = Field(gt=MIN_FULL_AMOUNT)
    comment: Optional[str] = None
    create_date: Optional[datetime] = None


class DonationFullInfoDB(InvestmentBase):
    id: int
    comment: Optional[str] = None
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)