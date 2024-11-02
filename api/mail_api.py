import smtplib

from fastapi import HTTPException
from models.contact_form import ContactForm
from settings import settings


class MailApi:
    def __init__(self):
        self.sender_email = settings.EMAIL_SENDER
        self.receiver_email = settings.EMAIL_RECEIVER
        self.password = settings.EMAIL_PASSWORD

    async def send_email(self, contact_form: ContactForm):
        try:
            message = "Subject: New Contact Us Message\n\n"
            message += f"Name: {contact_form.name}\n"
            message += f"Email: {contact_form.email}\n"
            message += f"Message:\n{contact_form.message}"

            with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email,
                                self.receiver_email, message)

            return {"message": "Email sent successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Failed to send email") from e


mail_api = MailApi()
