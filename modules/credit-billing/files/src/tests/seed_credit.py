"""Test helpers for credit billing (copied by credit_billing module)."""

from __future__ import annotations


async def seed_credit_balance(session, *, user_id: str, units: int) -> None:
    from db.credit_models import CreditBalance

    session.add(CreditBalance(user_id=user_id, units=units))
    await session.commit()
