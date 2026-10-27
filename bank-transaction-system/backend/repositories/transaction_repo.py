from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.transaction import Transaction


class TransactionRepository:
    @staticmethod
    def create(
        db: Session,
        account_id: UUID,
        type_: str,
        amount: Decimal,
        description: Optional[str],
        reference_id: str,
        transfer_id: Optional[UUID] = None,
    ) -> Transaction:
        transaction = Transaction(
            account_id=account_id,
            type=type_,
            amount=amount,
            description=description,
            reference_id=reference_id,
            transfer_id=transfer_id,
        )
        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def get_by_reference(db: Session, account_id: UUID, reference_id: str) -> Optional[Transaction]:
        return (
            db.query(Transaction)
            .filter(
                Transaction.account_id == account_id,
                Transaction.reference_id == reference_id,
            )
            .one_or_none()
        )

    @staticmethod
    def list_by_account(
        db: Session, account_id: UUID, page: int = 1, limit: int = 10
    ) -> Tuple[List[Transaction], int]:
        total = (
            db.query(func.count(Transaction.id))
            .filter(Transaction.account_id == account_id)
            .scalar()
            or 0
        )
        offset = (page - 1) * limit
        items = (
            db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    @staticmethod
    def list_recent(db: Session, limit: int = 10) -> List[Transaction]:
        return (
            db.query(Transaction)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .limit(limit)
            .all()
        )
