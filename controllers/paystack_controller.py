from fastapi import APIRouter, HTTPException, Request, Depends, status
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.schema import Payment
from api.paystack_api import paystack_api

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/initialize")
async def initialize_payment(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    amount = body.get('amount')
    email = body.get('email')
    callback_url = body.get('callbackUrl')
    name = body.get('name')

    payment_details = {
        "amount": amount,
        "email": email,
        "callback_url": callback_url,
        "metadata": {
            "amount": amount,
            "email": email,
            "name": name,
        }
    }

    data = await paystack_api.initialize_payment(payment_details)

    return {
        "message": "Payment initialized successfully",
        "data": data
    }


@router.get("/verify")
async def verify_payment(reference: str, db: Session = Depends(get_db)):
    if not reference:
        raise HTTPException(
            status_code=400, detail="Missing transaction reference")

    response = await paystack_api.verify_payment(reference)
    data = response['data']
    metadata = data['metadata']
    email = metadata['email']
    amount = metadata['amount']
    name = metadata['name']
    payment_reference = data['reference']
    transaction_status = data['status']

    if transaction_status != 'success':
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail=f"Transaction: {transaction_status}")

    payment_record = Payment(
        amount=amount,
        email=email,
        name=name,
        paymentReference=payment_reference
    )
    # Save payment_record to the database
    db.add(payment_record)
    db.commit()
    db.refresh(payment_record)

    return {
        "message": "Payment verified",
        "data": payment_record
    }
