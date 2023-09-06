from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from .utils import get_paypal_session

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

# TODO: Check out what payments are
#       https://developer.paypal.com/docs/api/payments/v2/
@router.get("/create")
def create_deposit():
    try:
        url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"

        payload = json.dumps({
        "intent": "CAPTURE",
        "purchase_units": [
            {
            "items": [
                {
                "name": "T-Shirt",
                "description": "Green XL",
                "quantity": "1",
                "unit_amount": {
                    "currency_code": "USD",
                    "value": "100.00"
                }
                }
            ],
            "amount": {
                "currency_code": "USD",
                "value": "100.00",
                "breakdown": {
                "item_total": {
                    "currency_code": "USD",
                    "value": "100.00"
                }
                }
            }, 
            # "payment_instruction": {
            #     "disbursement_mode": "INSTANT",
            #     "platform_fees": [
            #     {
            #         "amount": {
            #         "currency_code": "USD",
            #         "value": "25.00"
            #         }
            #     }
            #     ]
            # }
            }
        ],
        "application_context": {
            "return_url": "https://example.com/return",
            "cancel_url": "https://example.com/cancel"
        }
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + get_paypal_session(),
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        
        response.raise_for_status() 
        
        return response.json()
    except Exception as e:
        # Handle exceptions as needed
        print(e)

        # FIXME: not sure how to raise e actually
        # raise e
        pass

@router.get("/{deposit_id}")
def get_deposit(deposit_id: str):
    headers = {
        'Authorization': 'Bearer ' + get_paypal_session(),
    }

    # FIXME: deposit id doesnt mean transaction id, so how is this supposed to scale?
    #           Testing purposes: 4AC52781DN396583L
    response = requests.get('https://api-m.sandbox.paypal.com/v2/checkout/orders/' + deposit_id, headers=headers)

    return response.json()

    pass