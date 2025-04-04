from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from api.paystack_api import paystack_api
from database.database import SessionLocal
from sqlalchemy.orm import Session, joinedload

from database.schema import HostingPayment, HostingPlans
from models.hosting_payment_model import HostingPaymentModel, HostingPaymentResponse
from settings import settings

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/initialize")
async def initialize_payment(payment: HostingPaymentModel, db: Session = Depends(get_db)):
    try:
        email = payment.email
        full_name = payment.full_name
        phone = payment.phone

        hosting_plan = db.query(HostingPlans).filter(
            HostingPlans.id == payment.hosting_plan_id).first()

        if not hosting_plan:
            raise HTTPException(
                status_code=400, detail="Hosting plan not found")

        if not email or not full_name:
            raise HTTPException(
                status_code=400, detail="Email and Name are required.")

        amount = hosting_plan.annual_price
        print(settings.CALLBACK_URL)

        payment_details = {
            "currency": "KES",
            "amount": amount * 100,
            "email": email,
            "callback_url": settings.CALLBACK_URL,
            "channels": ["mobile_money", "card"],
            "metadata": {
                "amount": amount,
                "email": email,
                "name": full_name,
                "phone": phone,
            }
        }

        data = await paystack_api.initialize_payment(payment_details)
        reference = data['data']['reference']

        # Create a new payment record
        payment_record = HostingPayment(
            email=email,
            full_name=full_name,
            paymentReference=reference,
            phone=phone,
            hosting_plan_id=hosting_plan.id,
            status="pending"
        )

        db.add(payment_record)
        db.commit()
        db.refresh(payment_record)
        return {
            "message": "Payment initialized successfully",
            "data": data
        }
    except Exception as e:
        print(f"Error initializing payment: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error initializing payment: {e}")


@router.get("/verify/{reference}")
async def verify_payment(reference: str, db: Session = Depends(get_db)):
    if not reference:
        raise HTTPException(
            status_code=400, detail="Missing transaction reference")

    try:
        response = await paystack_api.verify_payment(reference)
        data = response['data']
        metadata = data['metadata']
        email = metadata.get('email')
        amount = metadata.get('amount')
        full_name = metadata.get('full_name')
        payment_reference = data['reference']
        transaction_status = data['status']

        if transaction_status != 'success':
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail=f"Transaction: {transaction_status}")

        # Check for existing payment record
        existing_payment = db.query(HostingPayment).filter(
            HostingPayment.paymentReference == payment_reference).first()

        if existing_payment:
            # raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Payment reference already exists")
            return {
                "message": "Payment already exists",
                "data": existing_payment
            }

    except Exception as e:
        print(f"Error verifying payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify payment")


@router.get("/callback/{reference}")
async def payment_callback(reference: str, db: Session = Depends(get_db)):
    if not reference:
        raise HTTPException(
            status_code=400, detail="Missing transaction reference")

    try:
        # Verify payment with Paystack API to ensure status is valid
        paystack_response = await paystack_api.verify_payment(reference)
        payment_status = paystack_response['data']['status']

        if payment_status in ['success', 'abandoned']:
            payment_record = db.query(HostingPayment).filter(
                HostingPayment.paymentReference == reference
            ).first()

            if not payment_record:
                return JSONResponse(status_code=404, content={"message": "Payment not found"})

            payment_record.status = payment_status
            db.commit()
            db.refresh(payment_record)

            # Use jsonable_encoder to serialize the object
            serialized_payment = jsonable_encoder(payment_record)
            message = "Payment processed successfully" if payment_status == 'success' else "Payment abandoned"
            return JSONResponse(status_code=200, content={"message": message, "data": serialized_payment})

        return JSONResponse(status_code=400, content={"message": "Payment failed or not successful"})

    except Exception as e:
        print(f"Error handling payment callback: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process payment callback: {e}")


@router.get("/payments", response_model=List[HostingPaymentResponse])
async def get_payments(db: Session = Depends(get_db)):
    payments = db.query(HostingPayment).options(
        joinedload(HostingPayment.hosting_plan)).all()
    return payments
