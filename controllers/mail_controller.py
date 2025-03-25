from fastapi import APIRouter, HTTPException, Depends, Request
from api.mail_api import mail_api
from models.contact_form import ContactForm
from database.database import SessionLocal
from sqlalchemy.orm import Session
from database.schema import ContactForm as Form
from pydantic import ValidationError

import logging

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/contact")
async def send_email(contact_form: ContactForm):
    try:
        # Create message
        message = "Subject: New Contact Us Message\n\n"
        message += f"Name: {contact_form.name}\n"
        message += f"Email: {contact_form.email}\n"
        message += f"Message:\n{contact_form.message}"

        # Connect to the server and send the email
        await mail_api.send_email(contact_form)

        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to send email") from e


@router.post("/webgenerator-email")
async def webgenerator_email(request: Request, db: Session = Depends(get_db)):
    try:
        # Parse request JSON into a Pydantic model
        form_data = await request.json()
        logging.info(f"Received contact form: {form_data}")
        contact_form = ContactForm(**form_data)

        # Create message
        message = "Subject: New Contact Us Message\n\n"
        message += f"Name: {contact_form.name}\n"
        message += f"Email: {contact_form.email}\n"
        message += f"Message:\n{contact_form.message}"

        # Send the email
        await mail_api.send_email(contact_form)

        # Save the contact form to the database
        form = Form(
            name=contact_form.name,
            email=contact_form.email,
            message=contact_form.message
        )
        db.add(form)
        db.commit()
        db.refresh(form)

        return {"message": "Email sent successfully"}
    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail="Invalid form data")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process the request"
        )

# TODO: Method implementation incomplete
@router.post("/hosting-payment-confirmed")
async def hosting_payment_confirmed(request: Request):
    try:
        # Parse request JSON into a Pydantic model
        form_data = await request.json()
        logging.info(f"Received payment confirmation: {form_data}")

        # Send a confirmation email
        await mail_api.send_payment_confirmation(form_data)

        return {"message": "Payment confirmation email sent successfully"}
    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail="Invalid form data")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process the request"
        )
