from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.usage_admin_models import (
    EndpointPricingInfo,
    ListEndpointPricingResponse,
    UpsertEndpointPricingRequest,
    UpsertEndpointPricingResponse,
)
from db.auth import require_admin_key
from db.session import get_session
from db.usage_admin import list_endpoint_pricing, upsert_endpoint_pricing

router = APIRouter(prefix="/admin", include_in_schema=False)


def _pricing_info(row) -> EndpointPricingInfo:
    return EndpointPricingInfo(
        id=row.id,
        endpoint_key=row.endpoint_key,
        usage_units=row.usage_units,
        created_at=row.created_at,
    )


@router.post("/upsert-endpoint-pricing", response_model=UpsertEndpointPricingResponse)
async def admin_upsert_endpoint_pricing(
    body: UpsertEndpointPricingRequest,
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> UpsertEndpointPricingResponse:
    row, created = await upsert_endpoint_pricing(
        session,
        body.endpoint_key,
        body.usage_units,
    )
    return UpsertEndpointPricingResponse(
        pricing=_pricing_info(row),
        created=created,
    )


@router.post("/list-endpoint-pricing", response_model=ListEndpointPricingResponse)
async def admin_list_endpoint_pricing(
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> ListEndpointPricingResponse:
    rows = await list_endpoint_pricing(session)
    return ListEndpointPricingResponse(
        pricing=[_pricing_info(row) for row in rows],
    )
