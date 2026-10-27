import uuid
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(String(255), nullable=False)
    balance = Column(Numeric(18, 2), nullable=False, default=Decimal("0.00"), server_default=text("0.00"))
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_account_balance_non_negative"),
        CheckConstraint("length(trim(name)) > 0", name="check_account_name_non_empty"),
    )

    transactions = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="desc(Transaction.created_at)",
    )
    sent_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.source_account_id",
        back_populates="source_account",
    )
    received_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.destination_account_id",
        back_populates="destination_account",
    )
