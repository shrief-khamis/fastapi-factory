from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# DEV-ONLY DATA MIGRATION:
# Seeds a small endpoint-pricing catalog for local development/testing.
revision = "0003_seed_dev_usage_pricing"
down_revision = "0002_seed_dev_identity_data"
branch_labels = None
depends_on = None

_SEED_PRICING = [
    {"endpoint_key": "async.metered_sleep", "usage_units": 1},
    {"endpoint_key": "celery.metered_submit_job", "usage_units": 5},
    {"endpoint_key": "celery.metered_job_status", "usage_units": 1},
    {"endpoint_key": "celery.metered_job_result", "usage_units": 2},
]


def upgrade() -> None:
    table = sa.table(
        "usage_endpoint_pricing",
        sa.column("endpoint_key", sa.String(length=255)),
        sa.column("usage_units", sa.Integer()),
    )
    op.bulk_insert(table, _SEED_PRICING)


def downgrade() -> None:
    for item in _SEED_PRICING:
        op.execute(
            sa.text(
                "DELETE FROM usage_endpoint_pricing WHERE endpoint_key = :endpoint_key"
            ),
            {"endpoint_key": item["endpoint_key"]},
        )
