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
    {"user_id": "00000000-0000-0000-0000-000000000001", "units": 12},
    {"user_id": "00000000-0000-0000-0000-000000000002", "units": 8},
]

_SEED_BILLED_PRICING = [
    {"endpoint_key": "async.billed_sleep", "usage_units": 3},
    {"endpoint_key": "celery.billed_submit_job", "usage_units": 4},
    {"endpoint_key": "celery.billed_job_status", "usage_units": 1},
    {"endpoint_key": "celery.billed_job_result", "usage_units": 2},
]


def upgrade() -> None:
    balances_table = sa.table(
        "credit_balances",
        sa.column("user_id", sa.String(length=36)),
        sa.column("units", sa.Integer()),
    )
    pricing_table = sa.table(
        "usage_endpoint_pricing",
        sa.column("endpoint_key", sa.String(length=255)),
        sa.column("usage_units", sa.Integer()),
    )
    op.bulk_insert(balances_table, _SEED_BALANCES)
    op.bulk_insert(pricing_table, _SEED_BILLED_PRICING)


def downgrade() -> None:
    for item in _SEED_BILLED_PRICING:
        op.execute(
            sa.text(
                "DELETE FROM usage_endpoint_pricing WHERE endpoint_key = :endpoint_key"
            ),
            {"endpoint_key": item["endpoint_key"]},
        )
    for item in _SEED_BALANCES:
        op.execute(
            sa.text("DELETE FROM credit_balances WHERE user_id = :user_id"),
            {"user_id": item["user_id"]},
        )
