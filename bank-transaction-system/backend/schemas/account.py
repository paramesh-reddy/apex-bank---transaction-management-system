from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Non-empty account holder or account name")

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Account name cannot be empty or whitespace only.")
        return stripped


class AccountCreate(AccountBase):
    pass


class AccountResponse(BaseModel):
    id: UUID
    name: str
    balance: Decimal = Field(..., max_digits=18, decimal_places=2)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountListResponse(BaseModel):
    items: List[AccountResponse]
    total: int


class AccountSummaryResponse(BaseModel):
    total_accounts: int
    total_balance: Decimal
    total_transactions: int
