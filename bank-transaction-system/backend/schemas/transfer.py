from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas.transaction import TransactionResponse


class TransferCreate(BaseModel):
    source_account_id: UUID = Field(..., description="UUID of the sender/source account")
    destination_account_id: UUID = Field(..., description="UUID of the receiver/destination account")
    amount: Decimal = Field(..., description="Transfer amount, must be greater than zero and have at most 2 decimal places")
    reference_id: str = Field(..., min_length=1, max_length=255, description="Globally unique transfer reference ID")
    description: Optional[str] = Field(None, max_length=500, description="Optional description of the transfer")

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
        exponent = v.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places.")
        if v > Decimal("9999999999999999.99"):
            raise ValueError("Amount exceeds maximum supported limit.")
        return v


class TransferResponse(BaseModel):
    id: UUID
    reference_id: str
    source_account_id: UUID
    destination_account_id: UUID
    amount: Decimal = Field(..., max_digits=18, decimal_places=2)
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransferDetailResponse(BaseModel):
    transfer: TransferResponse
    source_transaction: TransactionResponse
    destination_transaction: TransactionResponse
    source_balance: Decimal = Field(..., max_digits=18, decimal_places=2)
    destination_balance: Decimal = Field(..., max_digits=18, decimal_places=2)
