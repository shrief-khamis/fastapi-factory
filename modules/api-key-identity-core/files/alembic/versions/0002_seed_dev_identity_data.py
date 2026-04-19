from __future__ import annotations

import hashlib

from alembic import op
import sqlalchemy as sa


# DEV-ONLY DATA MIGRATION:
# Seeds two test users and two test API keys for local development.
revision = "0002_seed_dev_identity_data"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

_DEV_SALT = "dev-api-key-salt"
_SEED_USERS = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "seed@example.com",
        "api_key_plaintext": "seed-api-key-plaintext",
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "email": "other@example.com",
        "api_key_plaintext": "other-user-api-key-plaintext",
    },
]


def _hash_key(plaintext: str) -> str:
    return hashlib.sha256(f"{_DEV_SALT}:{plaintext}".encode("utf-8")).hexdigest()


def upgrade() -> None:
    users_table = sa.table(
        "users",
        sa.column("id", sa.String(length=36)),
        sa.column("email", sa.String(length=255)),
    )
    api_keys_table = sa.table(
        "api_keys",
        sa.column("user_id", sa.String(length=36)),
        sa.column("key_hash", sa.String(length=64)),
        sa.column("label", sa.String(length=255)),
    )

    op.bulk_insert(
        users_table,
        [{"id": item["id"], "email": item["email"]} for item in _SEED_USERS],
    )
    op.bulk_insert(
        api_keys_table,
        [
            {
                "user_id": item["id"],
                "key_hash": _hash_key(item["api_key_plaintext"]),
                "label": "seed-dev",
            }
            for item in _SEED_USERS
        ],
    )


def downgrade() -> None:
    user_ids = [item["id"] for item in _SEED_USERS]
    for user_id in user_ids:
        op.execute(
            sa.text("DELETE FROM api_keys WHERE user_id = :user_id AND label = 'seed-dev'"),
            {"user_id": user_id},
        )
    op.execute(
        sa.text("DELETE FROM users WHERE id IN :ids").bindparams(
            sa.bindparam("ids", expanding=True)
        ),
        {"ids": user_ids},
    )
