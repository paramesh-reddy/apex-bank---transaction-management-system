from decimal import Decimal
from typing import Tuple
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from core.exceptions import (
    AccountNotFoundError,
    InsufficientBalanceError,
    DuplicateTransferReferenceError,
    SameAccountTransferError,
)
from models.transfer import Transfer
from models.transaction import Transaction
from repositories.account_repo import AccountRepository
from repositories.transaction_repo import TransactionRepository
from repositories.transfer_repo import TransferRepository


class TransferService:
    @staticmethod
    def process_transfer(
        db: Session,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: Decimal,
        reference_id: str,
        description: str | None = None,
    ) -> Tuple[Transfer, Transaction, Transaction, Decimal, Decimal]:
        """Atomically transfers money from source account to destination account.

        Guarantees:
        1. Both accounts exist.
        2. Source and destination are distinct.
        3. Deadlock-free locking: row locks are acquired in strictly ordered UUID sequence.
        4. Atomic balance verification and debit/credit adjustments using Decimal arithmetic.
        5. Traceable debit and credit transactions linked to the transfer record.
        6. Complete rollback if any step fails.
        """
        if source_account_id == destination_account_id:
            raise SameAccountTransferError()

        try:
            with db.begin():
                # Acquire locks in deterministic ascending order to prevent deadlocks
                source_acc, dest_acc = AccountRepository.get_accounts_for_update_ordered(
                    db=db,
                    account_id_a=source_account_id,
                    account_id_b=destination_account_id,
                )

                if not source_acc:
                    raise AccountNotFoundError(str(source_account_id))
                if not dest_acc:
                    raise AccountNotFoundError(str(destination_account_id))

                source_balance = Decimal(str(source_acc.balance))
                dest_balance = Decimal(str(dest_acc.balance))

                if source_balance < amount:
                    raise InsufficientBalanceError(
                        f"Source account '{source_acc.name}' has insufficient funds. Available: {source_balance}, Requested transfer: {amount}."
                    )

                # Insert transfer record
                transfer = TransferRepository.create(
                    db=db,
                    reference_id=reference_id,
                    source_account_id=source_account_id,
                    destination_account_id=destination_account_id,
                    amount=amount,
                    description=description,
                )

                # Debit transaction on source account
                debit_desc = f"Transfer to {dest_acc.name}" + (f": {description}" if description else "")
                source_tx = TransactionRepository.create(
                    db=db,
                    account_id=source_account_id,
                    type_="debit",
                    amount=amount,
                    description=debit_desc,
                    reference_id=f"TR-DEBIT-{reference_id}",
                    transfer_id=transfer.id,
                )

                # Credit transaction on destination account
                credit_desc = f"Transfer from {source_acc.name}" + (f": {description}" if description else "")
                dest_tx = TransactionRepository.create(
                    db=db,
                    account_id=destination_account_id,
                    type_="credit",
                    amount=amount,
                    description=credit_desc,
                    reference_id=f"TR-CREDIT-{reference_id}",
                    transfer_id=transfer.id,
                )

                # Update both balances atomically
                new_source_balance = source_balance - amount
                new_dest_balance = dest_balance + amount

                AccountRepository.update_balance(db, account=source_acc, new_balance=new_source_balance)
                AccountRepository.update_balance(db, account=dest_acc, new_balance=new_dest_balance)

            return transfer, source_tx, dest_tx, new_source_balance, new_dest_balance

        except IntegrityError as exc:
            db.rollback()
            err_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
            if "transfers_reference_id_key" in err_msg or "reference_id" in err_msg:
                raise DuplicateTransferReferenceError(reference_id)
            raise
