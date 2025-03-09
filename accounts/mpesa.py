import requests
import base64
from django.conf import settings

def get_mpesa_access_token():
    # M-Pesa OAuth URL
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    # Encode consumer key and secret in Base64
    credentials = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    # Set headers
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    # Make the request
    response = requests.get(url, headers=headers)
    
    # Check for errors
    if response.status_code != 200:
        raise Exception(f"Failed to fetch access token: {response.status_code} - {response.text}")
    
    # Return the access token
    return response.json().get("access_token")