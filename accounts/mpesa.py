import requests
from django.conf import settings
import base64

def get_mpesa_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate"
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
        ).decode()
    }
    response = requests.get(url, headers=headers)
    return response.json().get("access_token")
