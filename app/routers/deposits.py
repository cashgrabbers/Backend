from fastapi import APIRouter, Depends, HTTPException

from ..config import settings
import json
import requests

from ..dependencies import poll_for_paypal_session

# Way it goes: 
router = APIRouter(
    prefix="/deposits",
    tags=["deposits"],
    dependencies=[Depends(poll_for_paypal_session)],
    responses={404: {"description": "Not found"}},
)

fake_deposits_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}

@router.get("/create")
def create_deposit():
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"

    payload = json.dumps({
    "intent": "CAPTURE",
    "purchase_units": [
        {
        "amount": {
            "currency_code": "USD",
            "value": "100.00"
        },
        "payee": {
            "email_address": "seller@example.com"
        },
        "payment_instruction": {
            "disbursement_mode": "INSTANT",
            "platform_fees": [
            {
                "amount": {
                "currency_code": "USD",
                "value": "25.00"
                }
            }
            ]
        }
        }
    ]
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer &lt;Access-Token&gt;',
    'PayPal-Partner-Attribution-Id': '&lt;BN-Code&gt;'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # Deposit to user wallet
    
    print(response.text)

@router.get("/{deposit_id}")
def get_deposit():
    pass


def get_paypal_session():
    try:
        url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

        payload = 'grant_type=client_credentials'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic '+ settings.PAYPAL_API_KEY,
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        data = response.json()
        api_key = data.get("access_token")
        if api_key:
            # Store the retrieved API key securely, e.g., in a database or environment variable
            # This is just a placeholder example
            # app.state.api_key = api_key
            return api_key
            
            pass
    except Exception as e:
        # Handle exceptions as needed
        pass