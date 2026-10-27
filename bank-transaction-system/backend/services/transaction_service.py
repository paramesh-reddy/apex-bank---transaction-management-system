from decimal import Decimal
from typing import List, Tuple
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from core.exceptions import (
    AccountNotFoundError,
    InsufficientBalanceError,
    DuplicateTransactionReferenceError,
    InvalidTransactionTypeError,
    InvalidPaginationError,
)
from models.transaction import Transaction
from repositories.account_repo import AccountRepository
from repositories.transaction_repo import TransactionRepository


class TransactionService:
    @staticmethod
    def process_transaction(
        db: Session,
        account_id: UUID,
        type_: str,
        amount: Decimal,
        description: str | None,
        reference_id: str,
    ) -> Tuple[Transaction, Decimal]:
        """Atomically processes a credit or debit transaction on an account.

        1. Begins a database transaction.
        2. Locks the account row using SELECT ... FOR UPDATE.
        3. Verifies account exists.
        4. Validates operation against current balance.
        5. Inserts immutable transaction record.
        6. Updates account balance using Decimal precision.
        7. Commits both changes together.
        Rolls back completely if any failure occurs.
        """
        if type_ not in ("credit", "debit"):
            raise InvalidTransactionTypeError(type_)

        try:
            with db.begin():
                # 1 & 2. Lock account row with FOR UPDATE
                account = AccountRepository.get_by_id(db, account_id=account_id, for_update=True)
                if not account:
                    raise AccountNotFoundError(str(account_id))

                # 4. Validate operation against balance
                current_balance = Decimal(str(account.balance))
                if type_ == "debit":
                    if current_balance < amount:
                        raise InsufficientBalanceError(
                            f"The account does not have sufficient funds. Available: {current_balance}, Requested debit: {amount}."
                        )
                    new_balance = current_balance - amount
                else:  # credit
                    new_balance = current_balance + amount

                # 5. Insert immutable transaction
                transaction = TransactionRepository.create(
                    db=db,
                    account_id=account_id,
                    type_=type_,
                    amount=amount,
                    description=description,
                    reference_id=reference_id,
                )

                # 6. Update account balance
                AccountRepository.update_balance(db, account=account, new_balance=new_balance)

            # Re-read or return updated balance
            return transaction, new_balance

        except IntegrityError as exc:
            db.rollback()
            # Check if reference_id unique constraint was violated
            err_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
            if "uq_account_reference" in err_msg or "reference_id" in err_msg:
                raise DuplicateTransactionReferenceError(reference_id)
            raise

    @staticmethod
    def list_account_transactions(
        db: Session,
        account_id: UUID,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[Transaction], int, int]:
        """Lists transactions for an account with pagination and checks for account existence."""
        if page < 1:
            raise InvalidPaginationError("Page parameter must be greater than or equal to 1.")
        if limit < 1:
            raise InvalidPaginationError("Limit parameter must be greater than or equal to 1.")
        if limit > 100:
            raise InvalidPaginationError("Limit parameter cannot exceed 100.")

        # Verify account exists
        account = AccountRepository.get_by_id(db, account_id=account_id)
        if not account:
            raise AccountNotFoundError(str(account_id))

        items, total_count = TransactionRepository.list_by_account(
            db=db,
            account_id=account_id,
            page=page,
            limit=limit,
        )

        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
        return items, total_count, total_pages

    @staticmethod
    def list_recent_transactions(db: Session, limit: int = 10) -> List[Transaction]:
        return TransactionRepository.list_recent(db=db, limit=limit)
