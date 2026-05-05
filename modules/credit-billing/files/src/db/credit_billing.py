from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.credit_models import CreditBalance, CreditLedgerEntry
from db.usage_metering import resolve_usage_units


async def resolve_available_balance(
    session: AsyncSession,
    *,
    user_id: str,
) -> int:
    stmt = select(CreditBalance.units).where(CreditBalance.user_id == user_id).limit(1)
    result = await session.execute(stmt)
    units = result.scalar_one_or_none()
    if units is None:
        return 0
    return units


async def has_sufficient_balance(
    session: AsyncSession,
    *,
    user_id: str,
    required_units: int,
) -> bool:
    if required_units <= 0:
        return True
    available = await resolve_available_balance(session, user_id=user_id)
    return available >= required_units


async def bill_user_for_endpoint(
    session: AsyncSession,
    *,
    user_id: str,
    endpoint_key: str,
    ref: str | None = None,
) -> tuple[bool, int | None]:
    usage_units = await resolve_usage_units(session, endpoint_key)
    if usage_units is None:
        return True, None

    if usage_units < 0:
        raise ValueError("usage units must be non-negative")

    if not await has_sufficient_balance(
        session,
        user_id=user_id,
        required_units=usage_units,
    ):
        return False, usage_units

    stmt = select(CreditBalance).where(CreditBalance.user_id == user_id).limit(1)
    result = await session.execute(stmt)
    balance = result.scalar_one_or_none()
    if balance is None:
        balance = CreditBalance(user_id=user_id, units=0)
        session.add(balance)
        await session.flush()

    balance.units -= usage_units
    session.add(
        CreditLedgerEntry(
            user_id=user_id,
            delta_units=-usage_units,
            reason=f"billing:{endpoint_key}",
            ref=ref,
        )
    )
    await session.commit()
    return True, usage_units
