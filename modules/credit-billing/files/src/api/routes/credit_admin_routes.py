from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.credit_admin_models import (
    AddCreditRequest,
    AddCreditResponse,
    DeductCreditRequest,
    DeductCreditResponse,
    InspectCreditBalanceRequest,
    InspectCreditBalanceResponse,
    ListTopCreditBalancesRequest,
    ListTopCreditBalancesResponse,
    TopCreditBalanceInfo,
)
from db.auth import require_admin_key
from db.credit_admin import (
    add_credit,
    deduct_credit,
    inspect_credit_balance,
    list_top_credit_balances,
)
from db.identity_admin import get_user_by_email
from db.session import get_session

router = APIRouter(prefix="/admin", include_in_schema=False)


@router.post("/inspect-credit-balance", response_model=InspectCreditBalanceResponse)
async def admin_inspect_credit_balance(
    body: InspectCreditBalanceRequest,
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> InspectCreditBalanceResponse:
    user = await get_user_by_email(session, body.email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    balance = await inspect_credit_balance(session, user.id)
    return InspectCreditBalanceResponse(
        user_id=user.id,
        email=user.email,
        balance=balance,
    )


@router.post("/add-credit", response_model=AddCreditResponse)
async def admin_add_credit(
    body: AddCreditRequest,
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> AddCreditResponse:
    user = await get_user_by_email(session, body.email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    balance = await add_credit(session, user.id, body.units)
    return AddCreditResponse(
        user_id=user.id,
        email=user.email,
        balance=balance.units,
        added_units=body.units,
    )


@router.post("/deduct-credit", response_model=DeductCreditResponse)
async def admin_deduct_credit(
    body: DeductCreditRequest,
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> DeductCreditResponse:
    user = await get_user_by_email(session, body.email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    balance, deducted_units = await deduct_credit(session, user.id, body.units)
    return DeductCreditResponse(
        user_id=user.id,
        email=user.email,
        balance=balance.units,
        deducted_units=deducted_units,
    )


@router.post("/list-top-credit-balances", response_model=ListTopCreditBalancesResponse)
async def admin_list_top_credit_balances(
    body: ListTopCreditBalancesRequest,
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> ListTopCreditBalancesResponse:
    rows = await list_top_credit_balances(session, body.limit)
    return ListTopCreditBalancesResponse(
        balances=[
            TopCreditBalanceInfo(user_id=user_id, email=email, balance=units)
            for user_id, email, units in rows
        ],
    )
