from pydantic import BaseModel, EmailStr, Field, field_validator


class InspectCreditBalanceRequest(BaseModel):
    email: EmailStr


class InspectCreditBalanceResponse(BaseModel):
    user_id: str
    email: EmailStr
    balance: int


class AddCreditRequest(BaseModel):
    email: EmailStr
    units: int = Field(gt=0)


class AddCreditResponse(BaseModel):
    user_id: str
    email: EmailStr
    balance: int
    added_units: int


class DeductCreditRequest(BaseModel):
    email: EmailStr
    units: int | None = None

    @field_validator("units")
    @classmethod
    def units_positive_when_set(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("units must be greater than zero")
        return value


class DeductCreditResponse(BaseModel):
    user_id: str
    email: EmailStr
    balance: int
    deducted_units: int


class ListTopCreditBalancesRequest(BaseModel):
    limit: int = Field(default=10, gt=0, le=100)


class TopCreditBalanceInfo(BaseModel):
    user_id: str
    email: EmailStr
    balance: int


class ListTopCreditBalancesResponse(BaseModel):
    balances: list[TopCreditBalanceInfo]
