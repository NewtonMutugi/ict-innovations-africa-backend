from typing import List
from fastapi import APIRouter, Depends, HTTPException
from database.database import SessionLocal
from sqlalchemy.orm import Session, joinedload

from database.schema import HostingPlanFeatures, HostingPlans
from models.hosting_model import HostingPlansCreate, HostingPlansResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/hosting_plans", response_model=List[HostingPlansResponse])
def get_all_hosting_plans(db: Session = Depends(get_db)):
    """Get all hostng plans"""
    hosting_plans = db.query(HostingPlans).all()
    for plan in hosting_plans:
        plan.features = db.query(HostingPlanFeatures).filter(
            HostingPlanFeatures.hosting_plan_id == plan.id).all()
    return hosting_plans


@router.get("/hosting_plan/{hosting_plan_id}", response_model=HostingPlansResponse)
def get_hosting_plan(hosting_plan_id: int, db: Session = Depends(get_db)):
    """Get a single hosting plan"""
    hosting_plan = db.query(HostingPlans).filter(
        HostingPlans.id == hosting_plan_id).first()

    if not hosting_plan:
        raise HTTPException(status_code=404, detail="Hosting plan not found")

    hosting_plan.features = db.query(HostingPlanFeatures).filter(
        HostingPlanFeatures.hosting_plan_id == hosting_plan.id).all()
    return hosting_plan


@router.post("/hosting_plan")
def create_hosting_plan(hosting_plan: HostingPlansCreate, db: Session = Depends(get_db)):
    """Create Hosting Plan"""
    if not hosting_plan:
        raise HTTPException(status_code=400, detail="Hosting Plan invalid")

    existing_hosting_plan = db.query(HostingPlans).filter(
        HostingPlans.title == hosting_plan.title).first()

    if existing_hosting_plan:
        raise HTTPException(status_code=400, detail="Plan already exists")

    db_hosting_plan = HostingPlans(
        title=hosting_plan.title,
        monthly_price=hosting_plan.monthly_price,
        annual_price=hosting_plan.annual_price,
        subtitle=hosting_plan.subtitle,
    )
    db.add(db_hosting_plan)
    db.commit()
    db.refresh(db_hosting_plan)

    for feature in hosting_plan.features:
        db_feature = HostingPlanFeatures(
            hosting_plan_id=db_hosting_plan.id,
            feature=feature.feature
        )
        db.add(db_feature)

    db.commit()
    db.refresh(db_hosting_plan)

    return db_hosting_plan


@router.delete("/hosting_plan/{hosting_plan_id}", status_code=204)
def delete_hosting_plan(hosting_plan_id: int, db: Session = Depends(get_db)):
    """Delete hosting plan"""
    hosting_plan = db.query(HostingPlans).filter(
        HostingPlans.id == hosting_plan_id).first()

    if not hosting_plan:
        return HTTPException(status_code=404, detail="Hosting plan not found")
    return {"message": "Hosting Plan deleted successfully"}
