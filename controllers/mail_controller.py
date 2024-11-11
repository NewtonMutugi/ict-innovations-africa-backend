from fastapi import APIRouter, HTTPException, Depends, Request
from api.mail_api import mail_api
from models.contact_form import ContactForm
from database.database import SessionLocal
from sqlalchemy.orm import Session
from database.schema import ContactForm as Form
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
        mail_api.send_email(contact_form)

        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to send email") from e


@router.post("/webgenerator-email")
async def webgenerator_email(request: Request, db: Session = Depends(get_db)):
    try:
        contact_form = await request.json()
        logging.info(f"Received contact form: {contact_form}")
        print(f"Received contact form: {contact_form}")

        # Create message
        message = "Subject: New Contact Us Message\n\n"
        message += f"Name: {contact_form.name}\n"
        message += f"Email: {contact_form.email}\n"
        message += f"Message:\n{contact_form.message}"

        # Connect to the server and send the email
        mail_api.send_email(contact_form)

        # Save the contact form to the database
        form = Form(name=contact_form.name,
                    email=contact_form.email, message=contact_form.message)
        db.add(form)
        db.commit()
        db.refresh(contact_form)

        return {"message": "Email sent successfully"}
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to send email") from e
