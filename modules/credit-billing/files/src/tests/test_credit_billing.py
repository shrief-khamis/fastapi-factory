"""Unit tests for credit billing DB helpers."""

from conftest_db import TEST_USER_ID
from seed_credit import seed_credit_balance
from seed_usage import seed_usage_pricing
from db.credit_billing import bill_user_for_endpoint, has_sufficient_balance
from db.credit_models import CreditBalance, CreditLedgerEntry
from sqlalchemy import func, select


async def test_has_sufficient_balance_false_when_empty(seeded_db) -> None:
    assert (
        await has_sufficient_balance(
            seeded_db, user_id=TEST_USER_ID, required_units=1
        )
        is False
    )


async def test_bill_user_for_endpoint_returns_false_when_insufficient(seeded_db) -> None:
    await seed_usage_pricing(
        seeded_db, endpoint_key="async.billed_sleep", usage_units=5
    )
    await seed_credit_balance(seeded_db, user_id=TEST_USER_ID, units=2)

    billed, required = await bill_user_for_endpoint(
        seeded_db,
        user_id=TEST_USER_ID,
        endpoint_key="async.billed_sleep",
    )
    assert billed is False
    assert required == 5


async def test_bill_user_for_endpoint_deducts_balance_and_writes_ledger(seeded_db) -> None:
    await seed_usage_pricing(
        seeded_db, endpoint_key="async.billed_sleep", usage_units=3
    )
    await seed_credit_balance(seeded_db, user_id=TEST_USER_ID, units=10)

    billed, required = await bill_user_for_endpoint(
        seeded_db,
        user_id=TEST_USER_ID,
        endpoint_key="async.billed_sleep",
    )
    assert billed is True
    assert required == 3

    balance = await seeded_db.scalar(
        select(CreditBalance.units).where(CreditBalance.user_id == TEST_USER_ID)
    )
    assert balance == 7

    ledger_count = await seeded_db.scalar(
        select(func.count()).select_from(CreditLedgerEntry)
    )
    assert ledger_count == 1
