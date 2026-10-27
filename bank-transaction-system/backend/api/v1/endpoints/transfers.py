from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.transfer import (
    TransferCreate,
    TransferDetailResponse,
    TransferResponse,
)
from schemas.error import ErrorResponse
from services.transfer_service import TransferService
from repositories.transfer_repo import TransferRepository

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post(
    "",
    response_model=TransferDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Transfer money between two accounts",
    description=(
        "Executes an atomic transfer between two distinct bank accounts. "
        "Locks both account rows in deterministic UUID order to prevent deadlocks under concurrency. "
        "Verifies source account balance, creates the transfer record, creates debit and credit transaction records, "
        "and updates both balances atomically."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Insufficient funds or same account transfer error"},
        404: {"model": ErrorResponse, "description": "Source or destination account not found"},
        409: {"model": ErrorResponse, "description": "Duplicate transfer reference ID"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_transfer(
    transfer_in: TransferCreate,
    db: Session = Depends(get_db),
):
    transfer, src_tx, dst_tx, src_bal, dst_bal = TransferService.process_transfer(
        db=db,
        source_account_id=transfer_in.source_account_id,
        destination_account_id=transfer_in.destination_account_id,
        amount=transfer_in.amount,
        reference_id=transfer_in.reference_id,
        description=transfer_in.description,
    )
    return {
        "transfer": transfer,
        "source_transaction": src_tx,
        "destination_transaction": dst_tx,
        "source_balance": src_bal,
        "destination_balance": dst_bal,
    }


@router.get(
    "",
    response_model=List[TransferResponse],
    status_code=status.HTTP_200_OK,
    summary="List recent transfers",
    description="Returns a list of transfer records ordered by creation date descending.",
)
def list_transfers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, _ = TransferRepository.list_transfers(db=db, page=page, limit=limit)
    return items
