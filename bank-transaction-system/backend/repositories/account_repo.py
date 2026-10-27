from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from models.account import Account
from models.transaction import Transaction


class AccountRepository:
    @staticmethod
    def get_by_id(db: Session, account_id: UUID, for_update: bool = False) -> Optional[Account]:
        query = db.query(Account).filter(Account.id == account_id)
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    @staticmethod
    def get_accounts_for_update_ordered(
        db: Session, account_id_a: UUID, account_id_b: UUID
    ) -> Tuple[Optional[Account], Optional[Account]]:
        """Deadlock prevention: Always lock account rows in deterministic ascending UUID order."""
        if str(account_id_a) < str(account_id_b):
            first_id, second_id = account_id_a, account_id_b
            a_is_first = True
        else:
            first_id, second_id = account_id_b, account_id_a
            a_is_first = False

        acc_first = db.query(Account).filter(Account.id == first_id).with_for_update().one_or_none()
        acc_second = db.query(Account).filter(Account.id == second_id).with_for_update().one_or_none()

        if a_is_first:
            return acc_first, acc_second
        return acc_second, acc_first

    @staticmethod
    def create(db: Session, name: str) -> Account:
        account = Account(
            name=name,
            balance=Decimal("0.00"),
        )
        db.add(account)
        db.flush()
        return account

    @staticmethod
    def update_balance(db: Session, account: Account, new_balance: Decimal) -> Account:
        account.balance = new_balance
        db.flush()
        return account

    @staticmethod
    def list_accounts(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[Account], int]:
        total = db.query(func.count(Account.id)).scalar() or 0
        items = (
            db.query(Account)
            .order_by(Account.created_at.desc(), Account.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total

    @staticmethod
    def get_summary(db: Session) -> Tuple[int, Decimal, int]:
        total_accounts = db.query(func.count(Account.id)).scalar() or 0
        total_balance = db.query(func.coalesce(func.sum(Account.balance), Decimal("0.00"))).scalar() or Decimal("0.00")
        total_transactions = db.query(func.count(Transaction.id)).scalar() or 0
        return total_accounts, Decimal(str(total_balance)), total_transactions
