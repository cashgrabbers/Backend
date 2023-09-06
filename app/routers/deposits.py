from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from .utils import (get_paypal_session, add_balance_to_wallet)
from sqlalchemy.orm import Session
from ..database import get_db
from .auth import get_current_user
from ..schemas import User, Wallet
from ..config import settings

import json
import requests

# Way it goes: 
router = APIRouter(
    prefix="/deposits",
    tags=["deposits"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create/{amount}")
def create_deposit(amount: float):
    try:
        url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"

        payload = json.dumps({
        "intent": "CAPTURE",
        "purchase_units": [
            {
            "items": [
                {
                "name": "Tiktok Wallet",
                "description": "Deposits",
                "quantity": "1",
                "unit_amount": {
                    "currency_code": "SGD",
                    "value": amount
                }
                }
            ],
            "amount": {
                "currency_code": "SGD",
                "value": amount,
                "breakdown": {
                "item_total": {
                    "currency_code": "SGD",
                    "value": amount,
                }
                }
            }, 
            }
        ],
        "application_context": {
            "return_url": settings.BUBBLE_APP_URL,
            # /?token=6XE1119589511225P&PayerID=TCW5FWJ89ZBZW
            "cancel_url": settings.BUBBLE_APP_URL
        }
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + get_paypal_session(),
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        
        response.raise_for_status() 
    
        return response.json().get('links')[1].get('href')
    
    except Exception as e:
        # Handle exceptions as needed
        print(e)

        # FIXME: not sure how to raise e actually
        # raise e
        pass

@router.post("/capture/{deposit_id}")
def capture_deposit(deposit_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Here we add to the wallet?  
    
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders/" + deposit_id + "/capture"

    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
    'Authorization': 'Bearer ' + get_paypal_session(),
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 201:
        # add to the wallet balance
        # add to the deposit table
        print(response.json().get('purchase_units')[0].get('amount').get('value'), response.json().get('purchase_units')[0].get('amount').get('currency_code')) #10.00 SGD
        
        amount = float(response.json().get('purchase_units')[0].get('amount').get('value'))
        # currency = response.json().get('purchase_units')[0].get('amount').get('currency_code')

        updated_wallet = add_balance_to_wallet(db, current_user.wallet.id, amount)
        return {"status": "success", "updated_balance": updated_wallet.balance}
    
    # Might need to change?
    return response.json()

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