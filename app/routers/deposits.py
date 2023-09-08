from fastapi import APIRouter, Depends, HTTPException
from .utils import (get_paypal_session, add_balance_to_wallet, create_deposit_transaction)
from sqlalchemy.orm import Session
from ..database import get_db
from .auth import get_current_user
from ..schemas import User, DepositRequest, CaptureRequest, DepositCreate
from ..config import settings


import json
import requests

# Way it goes: 
router = APIRouter(
    prefix="/deposits",
    tags=["deposits"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
def create_deposit(deposit_request: DepositRequest):
    amount = deposit_request.amount
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
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/capture")
def capture_deposit(capture_request: CaptureRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deposit_id = capture_request.deposit_id
    
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
        currency = response.json().get('purchase_units')[0].get('amount').get('currency_code')
        
        #  update wallet balance
        updated_wallet = add_balance_to_wallet(db, current_user.wallet.id, amount)
        
        #  Log the deposit transaction
        db_deposit = DepositCreate(
            receiver_wallet_id = current_user.wallet.id,
            amount = amount,
            currency = currency,
            paypal_order_id=deposit_id
        )
        deposit_entry = create_deposit_transaction(db, db_deposit)
        
        return {"status": "success", "updated_balance": updated_wallet.balance, "deposit_entry": deposit_entry}

    return response.json()
