from fastapi import APIRouter
from controllers.paystack_controller import router as paystack_router

router = APIRouter()

router.include_router(paystack_router, prefix="/paystack", tags=["paystack"])
