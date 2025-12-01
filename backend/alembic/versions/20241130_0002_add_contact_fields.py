"""Add contact fields to domains table."""

from alembic import op
import sqlalchemy as sa


revision = "20241130_0002"
down_revision = "20241113_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add contact-related columns to domains table
    op.add_column("domains", sa.Column("contact_page_url", sa.String(length=512), nullable=True))
    op.add_column("domains", sa.Column("contact_check_status", sa.String(length=32), nullable=True))
    op.add_column("domains", sa.Column("contact_checked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("domains", sa.Column("contact_check_message", sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove contact-related columns
    op.drop_column("domains", "contact_check_message")
    op.drop_column("domains", "contact_checked_at")
    op.drop_column("domains", "contact_check_status")
    op.drop_column("domains", "contact_page_url")



