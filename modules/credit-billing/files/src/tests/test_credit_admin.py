"""Unit tests for credit admin DB helpers (balance math, ledger, ordering)."""

from conftest_db import TEST_USER_ID
from db.credit_admin import (
    add_credit,
    deduct_credit,
    inspect_credit_balance,
    list_top_credit_balances,
)
from db.credit_models import CreditLedgerEntry
from db.models import User
from seed_credit import seed_credit_balance
from sqlalchemy import func, select


async def test_inspect_credit_balance_returns_zero_when_missing(seeded_db) -> None:
    balance = await inspect_credit_balance(seeded_db, TEST_USER_ID)
    assert balance == 0


async def test_add_credit_creates_balance_and_ledger(seeded_db) -> None:
    balance = await add_credit(seeded_db, TEST_USER_ID, 10)
    assert balance.units == 10

    ledger_count = await seeded_db.scalar(
        select(func.count()).select_from(CreditLedgerEntry)
    )
    assert ledger_count == 1


async def test_deduct_credit_caps_at_current_balance(seeded_db) -> None:
    await seed_credit_balance(seeded_db, user_id=TEST_USER_ID, units=5)

    balance, deducted = await deduct_credit(seeded_db, TEST_USER_ID, 20)
    assert deducted == 5
    assert balance.units == 0


async def test_deduct_credit_all_when_units_none(seeded_db) -> None:
    await seed_credit_balance(seeded_db, user_id=TEST_USER_ID, units=7)

    balance, deducted = await deduct_credit(seeded_db, TEST_USER_ID, None)
    assert deducted == 7
    assert balance.units == 0


async def test_list_top_credit_balances_orders_by_balance(seeded_db) -> None:
    other_user = User(id="00000000-0000-0000-0000-000000000099", email="other@example.com")
    seeded_db.add(other_user)
    await seeded_db.commit()

    await seed_credit_balance(seeded_db, user_id=TEST_USER_ID, units=3)
    await seed_credit_balance(seeded_db, user_id=other_user.id, units=9)

    rows = await list_top_credit_balances(seeded_db, limit=2)
    assert rows[0][2] == 9
    assert rows[1][2] == 3
