from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import (
    MIN_FULL_AMOUNT, MAX_LENGTH_NAME_PROJECT, MIN_LENGTH_NAME_PROJECT,
    MIN_LENGTH_DESCRIPTION
)
from app.schemas.base import InvestmentBase


class CharityProjectDB(InvestmentBase):
    id: int
    name: str = Field(min_length=MIN_LENGTH_NAME_PROJECT,
                      max_length=MAX_LENGTH_NAME_PROJECT)
    description: str = Field(min_length=MIN_LENGTH_DESCRIPTION)
    model_config = ConfigDict(from_attributes=True)


class CharityProjectCreate(BaseModel):
    name: str = Field(min_length=MIN_LENGTH_NAME_PROJECT,
                      max_length=MAX_LENGTH_NAME_PROJECT)
    description: str = Field(min_length=MIN_LENGTH_DESCRIPTION)
    full_amount: int = Field(gt=MIN_FULL_AMOUNT)
    model_config = ConfigDict(extra='forbid')


class CharityProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=MIN_LENGTH_NAME_PROJECT,
                                max_length=MAX_LENGTH_NAME_PROJECT)
    description: Optional[str] = Field(None, min_length=MIN_LENGTH_DESCRIPTION)
    full_amount: Optional[int] = Field(None, gt=MIN_FULL_AMOUNT)
    model_config = ConfigDict(extra='forbid')

    @field_validator('name')
    @classmethod
    def name_cannot_be_null(cls, value):
        if value is None:
            error = 'Имя проекта не может быть пустым!'
            raise ValueError(error)
        return value