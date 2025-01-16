from fastapi import APIRouter
from controllers.paystack_controller import router as paystack_router
from controllers.mail_controller import router as mail_router
from controllers.events_controller import router as event_router
from controllers.auth_controller import router as auth_router
from controllers.hosting_plans_controller import router as hosting_plans_router
from controllers.hosting_payment_controller import router as hosting_payments_router

router = APIRouter()

router.include_router(paystack_router, prefix="/paystack", tags=["paystack"])
router.include_router(mail_router, prefix="/mail", tags=["mail"])
router.include_router(event_router, tags=["event"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(hosting_plans_router, tags=["hosting plans"])
router.include_router(hosting_payments_router, tags=["hosting payments"])
