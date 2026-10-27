from decimal import Decimal
from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from core.exceptions import AccountNotFoundError
from models.account import Account
from repositories.account_repo import AccountRepository


class AccountService:
    @staticmethod
    def create_account(db: Session, name: str) -> Account:
        with db.begin():
            return AccountRepository.create(db, name=name.strip())

    @staticmethod
    def get_account(db: Session, account_id: UUID) -> Account:
        account = AccountRepository.get_by_id(db, account_id=account_id)
        if not account:
            raise AccountNotFoundError(str(account_id))
        return account

    @staticmethod
    def list_accounts(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[Account], int]:
        return AccountRepository.list_accounts(db, skip=skip, limit=limit)

    @staticmethod
    def get_summary(db: Session) -> Tuple[int, Decimal, int]:
        return AccountRepository.get_summary(db)
