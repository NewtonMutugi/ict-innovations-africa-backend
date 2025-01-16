from typing import List
from pydantic import BaseModel


class HostingPlanFeature(BaseModel):
    feature: str


class HostingPlanFeatureResponse(HostingPlanFeature):
    id: int

    class Config:
        orm_mode = True


class HostingPlansModel(BaseModel):
    id: int
    title: str
    subtitle: str
    annual_price: float
    monthly_price: float

    class Config:
        orm_mode = True


class HostingPlansCreate(HostingPlansModel):
    features: List[HostingPlanFeature]


class HostingPlansResponse(HostingPlansModel):
    features: List[HostingPlanFeatureResponse] = []

    class Config:
        orm_mode = True
