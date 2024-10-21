from pydantic import BaseModel
from datetime import datetime


class PaymentSchema(BaseModel):
    name: str
    email: str
    amount: float
    currency: str
    paymentReference: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        orm_mode = True
