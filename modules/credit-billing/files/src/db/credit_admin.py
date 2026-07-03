from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.credit_billing import resolve_available_balance
from db.credit_models import CreditBalance, CreditLedgerEntry
from db.models import User


async def inspect_credit_balance(session: AsyncSession, user_id: str) -> int:
    return await resolve_available_balance(session, user_id=user_id)


async def _get_or_create_balance(
    session: AsyncSession, user_id: str
) -> CreditBalance:
    stmt = select(CreditBalance).where(CreditBalance.user_id == user_id).limit(1)
    result = await session.execute(stmt)
    balance = result.scalars().first()
    if balance is None:
        balance = CreditBalance(user_id=user_id, units=0)
        session.add(balance)
        await session.flush()
    return balance


async def add_credit(
    session: AsyncSession,
    user_id: str,
    units: int,
) -> CreditBalance:
    if units <= 0:
        raise ValueError("units must be greater than zero")

    balance = await _get_or_create_balance(session, user_id)
    balance.units += units
    session.add(
        CreditLedgerEntry(
            user_id=user_id,
            delta_units=units,
            reason="admin:add-credit",
        )
    )
    await session.commit()
    await session.refresh(balance)
    return balance


async def deduct_credit(
    session: AsyncSession,
    user_id: str,
    units: int | None,
) -> tuple[CreditBalance, int]:
    """
    Deduct credits from a user balance.

    When units is None, deduct the entire balance.
    When units is set, deduct min(units, current balance).

    Returns (balance, deducted_units).
    """
    if units is not None and units <= 0:
        raise ValueError("units must be greater than zero when provided")

    balance = await _get_or_create_balance(session, user_id)
    current = balance.units
    to_deduct = current if units is None else min(units, current)

    if to_deduct > 0:
        balance.units -= to_deduct
        session.add(
            CreditLedgerEntry(
                user_id=user_id,
                delta_units=-to_deduct,
                reason="admin:deduct-credit",
            )
        )

    await session.commit()
    await session.refresh(balance)
    return balance, to_deduct


async def list_top_credit_balances(
    session: AsyncSession,
    limit: int,
) -> list[tuple[str, str, int]]:
    """Return (user_id, email, balance) rows ordered by balance descending."""
    stmt = (
        select(User.id, User.email, CreditBalance.units)
        .join(CreditBalance, CreditBalance.user_id == User.id)
        .order_by(CreditBalance.units.desc(), User.email.asc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [(user_id, email, units) for user_id, email, units in result.all()]
