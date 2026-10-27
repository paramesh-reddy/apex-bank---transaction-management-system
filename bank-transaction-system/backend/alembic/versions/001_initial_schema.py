"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Accounts Table
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("balance", sa.Numeric(precision=18, scale=2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("balance >= 0", name="check_account_balance_non_negative"),
        sa.CheckConstraint("length(trim(name)) > 0", name="check_account_name_non_empty"),
        sa.PrimaryKeyConstraint("id", name="pk_accounts"),
    )

    # 2. Transfers Table
    op.create_table(
        "transfers",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("reference_id", sa.String(length=255), nullable=False),
        sa.Column("source_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("destination_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("source_account_id != destination_account_id", name="check_transfer_different_accounts"),
        sa.CheckConstraint("amount > 0", name="check_transfer_amount_positive"),
        sa.ForeignKeyConstraint(["source_account_id"], ["accounts.id"], ondelete="RESTRICT", name="fk_transfers_source_account"),
        sa.ForeignKeyConstraint(["destination_account_id"], ["accounts.id"], ondelete="RESTRICT", name="fk_transfers_dest_account"),
        sa.PrimaryKeyConstraint("id", name="pk_transfers"),
        sa.UniqueConstraint("reference_id", name="uq_transfers_reference_id"),
    )
    op.create_index("ix_transfers_source", "transfers", ["source_account_id"])
    op.create_index("ix_transfers_dest", "transfers", ["destination_account_id"])

    # 3. Transactions Table
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reference_id", sa.String(length=255), nullable=False),
        sa.Column("transfer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("type IN ('credit', 'debit')", name="check_transaction_type"),
        sa.CheckConstraint("amount > 0", name="check_transaction_amount_positive"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="RESTRICT", name="fk_transactions_account"),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"], ondelete="SET NULL", name="fk_transactions_transfer"),
        sa.PrimaryKeyConstraint("id", name="pk_transactions"),
        sa.UniqueConstraint("account_id", "reference_id", name="uq_account_reference"),
    )
    op.create_index(
        "ix_transactions_account_created",
        "transactions",
        ["account_id", sa.text("created_at DESC")],
    )

    # 4. Database-level transaction immutability trigger
    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_transaction_modification()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'Transactions are strictly immutable and cannot be updated or deleted.';
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_prevent_transaction_update_delete ON transactions;
    CREATE TRIGGER trg_prevent_transaction_update_delete
    BEFORE UPDATE OR DELETE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION prevent_transaction_modification();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_transaction_update_delete ON transactions;")
    op.execute("DROP FUNCTION IF EXISTS prevent_transaction_modification();")
    op.drop_table("transactions")
    op.drop_table("transfers")
    op.drop_table("accounts")
