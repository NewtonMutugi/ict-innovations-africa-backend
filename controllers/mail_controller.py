from fastapi import APIRouter, HTTPException, Depends
from api.mail_api import mail_api
from database.schema import ContactForm
from database.database import SessionLocal
from sqlalchemy.orm import Session

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
async def webgenerator_email(contact_form: ContactForm, db: Session = Depends(get_db)):
    try:
        # Create message
        message = "Subject: New Contact Us Message\n\n"
        message += f"Name: {contact_form.name}\n"
        message += f"Email: {contact_form.email}\n"
        message += f"Message:\n{contact_form.message}"

        # Connect to the server and send the email
        mail_api.send_email(contact_form)

        db.add(contact_form)
        db.commit()
        db.refresh(contact_form)

        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to send email") from e
