from fastapi import APIRouter, HTTPException, Request, Depends, status
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.schema import Payment
from api.paystack_api import paystack_api

router = APIRouter()

# Constants
PAYMENT_AMOUNT = 1000
CALLBACK_URL = "https://yourdomain.com/callback"

# Dependency for database session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/initialize")
async def initialize_payment(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        amount = PAYMENT_AMOUNT
        email = body.get('email')
        name = body.get('name')
        phone = body.get('phone')

        if not email or not name:
            raise HTTPException(
                status_code=400, detail="Email and Name are required.")

        payment_details = {
            "amount": amount,
            "email": email,
            # "callback_url": CALLBACK_URL,
            "metadata": {
                "amount": amount,
                "email": email,
                "name": name,
                "phone": phone
            }
        }

        data = await paystack_api.initialize_payment(payment_details)
        reference = data['data']['reference']

        # Create a new payment record
        payment_record = Payment(
            amount=amount,
            email=email,
            name=name,
            paymentReference=reference,
            phone=phone,
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
            status_code=500, detail="Failed to initialize payment")


@router.get("/verify")
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
        name = metadata.get('name')
        payment_reference = data['reference']
        transaction_status = data['status']

        if transaction_status != 'success':
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail=f"Transaction: {transaction_status}")

        # Check for existing payment record
        existing_payment = db.query(Payment).filter(
            Payment.paymentReference == payment_reference).first()

        if existing_payment:
            # raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Payment reference already exists")
            return {
                "message": "Payment already exists",
                "data": existing_payment
            }

        # Create a new payment record
        # payment_record = Payment(
        #     amount=amount,
        #     email=email,
        #     name=name,
        #     paymentReference=payment_reference,
        #     phone=metadata.get('phone'),
        # )

        # db.add(payment_record)
        # db.commit()
        # db.refresh(payment_record)

        # return {
        #     "message": "Payment verified",
        #     "data": payment_record
        # }

    except Exception as e:
        print(f"Error verifying payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify payment")


@router.post("/callback")
async def payment_callback(request: Request, db: Session = Depends(get_db)):
    try:
        callback_data = await request.json()
        reference = callback_data.get("reference")
        status = callback_data.get("status")

        if not reference or not status:
            raise HTTPException(
                status_code=400, detail="Invalid callback data"
            )

        # Verify payment with Paystack API to ensure status is valid
        paystack_response = await paystack_api.verify_payment(reference)

        if paystack_response['data']['status'] == 'success':
            # Confirm the payment, update the database
            payment_record = db.query(Payment).filter(
                Payment.paymentReference == reference
            ).first()

            if payment_record:
                payment_record.status = "completed"
                db.commit()
                return {"message": "Payment processed successfully", "data": payment_record}
            else:
                return {"message": "Payment not found"}

        return {"message": "Payment failed or not successful"}

    except Exception as e:
        print(f"Error handling payment callback: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process payment callback"
        )
