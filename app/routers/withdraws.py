from fastapi import APIRouter, Depends
from .utils import get_paypal_session
from app.routers.routers import get_current_user
from ..models import Wallet
import json

import requests

from ..dependencies import poll_for_paypal_session

router = APIRouter(
    prefix="/withdraws",
    tags=["withdraws"],
    dependencies=[Depends(poll_for_paypal_session)],
    responses={404: {"description": "Not found"}},
)

# Define a route to access the retrieved API key
@router.get("/test_get_api_key")
def get_retrieved_api_key():
    return get_paypal_session()
    # return {"retrieved_api_key": getattr(router.state, "session_key", "Not available")}


@router.get("/create")
def create_withdraw(account: str, withdraw: Wallet = Depends(get_current_user)):
    url = "https://api-m.sandbox.paypal.com/v1/payments/payouts"

    payload = json.dumps({
    "sender_batch_header": {
        "sender_batch_id": "Payouts_1693969860",
        "email_subject": "You have a payout!",
        "email_message": "You have received a payout! Thanks for using our service!"
    },
    "items": [
        {
        "recipient_type": "EMAIL",
        "amount": {
            "value": "10.00",
            "currency": "USD"
        },
        "note": "Thanks for your patronage!",
        "sender_item_id": "201403140001",
        "receiver": "Nola_Rempel@hotmail.com",
        "notification_language": "en-US"
        },
        {
        "recipient_type": "PHONE",
        "amount": {
            "value": "20.00",
            "currency": "USD"
        },
        "note": "Thanks for your support!",
        "sender_item_id": "201403140002",
        "receiver": "1-868-872-5226"
        },
        {
        "recipient_type": "PAYPAL_ID",
        "amount": {
            "value": "30.00",
            "currency": "USD"
        },
        "note": "Thanks for your patronage!",
        "sender_item_id": "201403140003",
        "receiver": "5DEJUG27PZB9J"
        }
    ]
    })

    # FIXME: not sure why this is unauthorised
    #        Not sure how to generate request-id
    headers = {
    'Content-Type': 'application/json',
    'PayPal-Request-Id': '10eb74ec-358d-47c9-bfe9-d406ae0471f0',
    'Authorization': 'Bearer ' + get_paypal_session(),
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json
