import uuid
from decimal import Decimal
from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    type = Column(String(10), nullable=False)  # 'credit' or 'debit'
    amount = Column(Numeric(18, 2), nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(String(255), nullable=False)
    transfer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transfers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("account_id", "reference_id", name="uq_account_reference"),
        CheckConstraint("type IN ('credit', 'debit')", name="check_transaction_type"),
        CheckConstraint("amount > 0", name="check_transaction_amount_positive"),
        Index("ix_transactions_account_created", "account_id", text("created_at DESC")),
    )

    account = relationship("Account", back_populates="transactions")
    transfer = relationship("Transfer", back_populates="transactions")
