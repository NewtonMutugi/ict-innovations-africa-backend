import httpx
from settings import settings


class PaystackApi:
    def __init__(self):
        self.base_url = settings.PAYSTACK_BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'
        }

    async def initialize_payment(self, payment_details):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/transaction/initialize',
                json=payment_details,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def verify_payment(self, payment_reference):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/transaction/verify/{payment_reference}',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()


paystack_api = PaystackApi()
