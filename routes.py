from fastapi import APIRouter
from controllers.paystack_controller import router as paystack_router
from controllers.mail_controller import router as mail_router

router = APIRouter()

router.include_router(paystack_router, prefix="/paystack", tags=["paystack"])
router.include_router(mail_router, prefix="/mail", tags=["mail"])
