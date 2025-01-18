from datetime import datetime
from pydantic import BaseModel


class HostingPlanResponse(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True


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
    hosting_plan: HostingPlanResponse  # Include the nested model

    class Config:
        orm_mode = True
