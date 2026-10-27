from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID
import math
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransactionCreate(BaseModel):
    type: Literal["credit", "debit"] = Field(..., description="Type of transaction: 'credit' or 'debit'")
    amount: Decimal = Field(..., description="Transaction amount, must be greater than zero and have at most 2 decimal places")
    description: Optional[str] = Field(None, max_length=500, description="Optional description of the transaction")
    reference_id: str = Field(..., min_length=1, max_length=255, description="Unique reference ID for this transaction per account")

    @field_validator("reference_id")
    def validate_reference_id(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("reference_id cannot be empty or whitespace only.")
        return stripped

    @field_validator("amount")
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v.is_nan() or v.is_infinite():
            raise ValueError("Amount cannot be NaN or Infinite.")
        if v <= Decimal("0.00"):
            raise ValueError("Amount must be strictly greater than zero.")
        # Ensure at most 2 decimal places
        exponent = v.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places.")
        # Maximum allowed numeric value for NUMERIC(18,2)
        if v > Decimal("9999999999999999.99"):
            raise ValueError("Amount exceeds maximum supported transaction limit.")
        return v


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    type: str
    amount: Decimal = Field(..., max_digits=18, decimal_places=2)
    description: Optional[str]
    reference_id: str
    transfer_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionWithBalanceResponse(BaseModel):
    transaction: TransactionResponse
    account_balance: Decimal = Field(..., max_digits=18, decimal_places=2)


class PaginatedTransactionsResponse(BaseModel):
    items: List[TransactionResponse]
    current_page: int
    page_size: int
    total_records: int
    total_pages: int
