from datetime import datetime

from pydantic import BaseModel, Field


class UpsertEndpointPricingRequest(BaseModel):
    endpoint_key: str = Field(min_length=1, max_length=255)
    usage_units: int = Field(gt=0)


class EndpointPricingInfo(BaseModel):
    id: int
    endpoint_key: str
    usage_units: int
    created_at: datetime


class UpsertEndpointPricingResponse(BaseModel):
    pricing: EndpointPricingInfo
    created: bool


class ListEndpointPricingResponse(BaseModel):
    pricing: list[EndpointPricingInfo]
