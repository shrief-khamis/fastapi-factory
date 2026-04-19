from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# DEV-ONLY DATA MIGRATION:
# Seeds test credit balances for the two dev users.
revision = "0004_seed_dev_credit_balances"
down_revision = "0003_seed_dev_usage_pricing"
branch_labels = None
depends_on = None

_SEED_BALANCES = [
    {"user_id": "00000000-0000-0000-0000-000000000001", "units": 1000},
    {"user_id": "00000000-0000-0000-0000-000000000002", "units": 750},
]


def upgrade() -> None:
    table = sa.table(
        "credit_balances",
        sa.column("user_id", sa.String(length=36)),
        sa.column("units", sa.Integer()),
    )
    op.bulk_insert(table, _SEED_BALANCES)


def downgrade() -> None:
    for item in _SEED_BALANCES:
        op.execute(
            sa.text("DELETE FROM credit_balances WHERE user_id = :user_id"),
            {"user_id": item["user_id"]},
        )
