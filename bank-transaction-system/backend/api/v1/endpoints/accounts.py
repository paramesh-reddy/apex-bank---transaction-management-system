from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountListResponse,
    AccountSummaryResponse,
)
from schemas.transaction import (
    TransactionCreate,
    TransactionWithBalanceResponse,
    TransactionResponse,
    PaginatedTransactionsResponse,
)
from schemas.error import ErrorResponse
from services.account_service import AccountService
from services.transaction_service import TransactionService

router = APIRouter(prefix="/accounts", tags=["Accounts & Transactions"])


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank account",
    description="Creates a new account with an initial balance of 0.00. Account name must be non-empty.",
    responses={
        400: {"model": ErrorResponse, "description": "Validation or business error"},
        422: {"model": ErrorResponse, "description": "Unprocessable entity error"},
    },
)
def create_account(
    account_in: AccountCreate,
    db: Session = Depends(get_db),
):
    account = AccountService.create_account(db=db, name=account_in.name)
    return account


@router.get(
    "",
    response_model=AccountListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all bank accounts",
    description="Returns a list of accounts sorted by creation date descending.",
)
def list_accounts(
    skip: int = Query(0, ge=0, description="Offset number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    items, total = AccountService.list_accounts(db=db, skip=skip, limit=limit)
    return {"items": items, "total": total}


@router.get(
    "/summary/metrics",
    response_model=AccountSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated bank metrics",
    description="Returns total number of accounts, combined balances, and total transactions count directly calculated from PostgreSQL.",
)
def get_metrics_summary(
    db: Session = Depends(get_db),
):
    total_accounts, total_balance, total_transactions = AccountService.get_summary(db=db)
    return {
        "total_accounts": total_accounts,
        "total_balance": total_balance,
        "total_transactions": total_transactions,
    }


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get account details and current balance",
    description="Fetches account details by UUID. Returns 404 if account does not exist.",
    responses={
        404: {"model": ErrorResponse, "description": "Account not found"},
    },
)
def get_account(
    account_id: UUID,
    db: Session = Depends(get_db),
):
    return AccountService.get_account(db=db, account_id=account_id)


@router.post(
    "/{account_id}/transactions",
    response_model=TransactionWithBalanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a credit or debit transaction",
    description=(
        "Executes an atomic transaction for the specified account. "
        "Locks the account row, validates available balance for debits, inserts an immutable transaction record, "
        "and updates the account balance within the same database transaction. "
        "Prevents duplicate reference IDs for the same account."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Insufficient funds or invalid transaction parameters"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        409: {"model": ErrorResponse, "description": "Duplicate reference ID for this account"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_transaction(
    account_id: UUID,
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
):
    transaction, new_balance = TransactionService.process_transaction(
        db=db,
        account_id=account_id,
        type_=transaction_in.type,
        amount=transaction_in.amount,
        description=transaction_in.description,
        reference_id=transaction_in.reference_id,
    )
    return {
        "transaction": transaction,
        "account_balance": new_balance,
    }


@router.get(
    "/{account_id}/transactions",
    response_model=PaginatedTransactionsResponse,
    status_code=status.HTTP_200_OK,
    summary="List transactions for an account",
    description="Returns paginated transactions sorted in descending created_at order with a stable secondary sort by id.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid page or limit parameters"},
        404: {"model": ErrorResponse, "description": "Account not found"},
    },
)
def get_account_transactions(
    account_id: UUID,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Records per page (maximum 100)"),
    db: Session = Depends(get_db),
):
    items, total_records, total_pages = TransactionService.list_account_transactions(
        db=db,
        account_id=account_id,
        page=page,
        limit=limit,
    )
    return {
        "items": items,
        "current_page": page,
        "page_size": limit,
        "total_records": total_records,
        "total_pages": total_pages,
    }
