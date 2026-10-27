import uuid
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    reference_id = Column(String(255), nullable=False, unique=True, index=True)
    source_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    destination_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount = Column(Numeric(18, 2), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("source_account_id != destination_account_id", name="check_transfer_different_accounts"),
        CheckConstraint("amount > 0", name="check_transfer_amount_positive"),
    )

    source_account = relationship(
        "Account",
        foreign_keys=[source_account_id],
        back_populates="sent_transfers",
    )
    destination_account = relationship(
        "Account",
        foreign_keys=[destination_account_id],
        back_populates="received_transfers",
    )
    transactions = relationship(
        "Transaction",
        back_populates="transfer",
    )
