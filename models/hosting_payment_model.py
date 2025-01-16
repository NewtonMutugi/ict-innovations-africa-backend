from datetime import datetime
from pydantic import BaseModel


class HostingPaymentModel(BaseModel):
    email: str
    full_name: str
    phone: str
    hosting_plan_id: int

    class Config:
        orm_mode = True


class HostingPaymentResponse(HostingPaymentModel):
    id: int
    status: str
    paymentReference: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
