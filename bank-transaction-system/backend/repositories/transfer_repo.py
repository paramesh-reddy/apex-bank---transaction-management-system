from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.transfer import Transfer


class TransferRepository:
    @staticmethod
    def create(
        db: Session,
        reference_id: str,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> Transfer:
        transfer = Transfer(
            reference_id=reference_id,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            amount=amount,
            description=description,
        )
        db.add(transfer)
        db.flush()
        return transfer

    @staticmethod
    def get_by_id(db: Session, transfer_id: UUID) -> Optional[Transfer]:
        return db.query(Transfer).filter(Transfer.id == transfer_id).one_or_none()

    @staticmethod
    def get_by_reference(db: Session, reference_id: str) -> Optional[Transfer]:
        return db.query(Transfer).filter(Transfer.reference_id == reference_id).one_or_none()

    @staticmethod
    def list_transfers(db: Session, page: int = 1, limit: int = 20) -> Tuple[List[Transfer], int]:
        total = db.query(func.count(Transfer.id)).scalar() or 0
        offset = (page - 1) * limit
        items = (
            db.query(Transfer)
            .order_by(Transfer.created_at.desc(), Transfer.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total
