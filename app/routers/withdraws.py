from fastapi import APIRouter, Depends, HTTPException
from .utils import get_paypal_session, check_wallet_balance, deduct_amount_from_wallet, create_withdraw_transaction
from app.routers.routers import get_current_user
from ..models import User
from ..schemas import WithdrawRequest
import json
import uuid
from sqlalchemy.orm import Session
from ..database import get_db

import requests

router = APIRouter(
    prefix="/withdraws",
    tags=["withdraws"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
def create_withdraw(withdraw_request: WithdrawRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    url = "https://api-m.sandbox.paypal.com/v1/payments/payouts"
    amount = withdraw_request.amount
    account_email = user.email

    payload = json.dumps({
    "sender_batch_header": {
        "sender_batch_id": f"Payouts_{str(uuid.uuid4())}",
        "email_subject": "You have a payout!",
        "email_message": "You have received a payout! Thanks for using our service!",
    },
    "items": [
        {
        "recipient_type": "EMAIL",
        "amount": {
            "value": amount,
            "currency": "USD",
        },
        "note": "Thanks for your patronage!",
        "sender_item_id": str(uuid.uuid4()),
        "receiver": account_email,
        "notification_language": "en-US",
        },
    ],
    })

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + get_paypal_session(),
    }

    # Check wallet balance to see if there is sufficient balance first
    if not check_wallet_balance(db, user.id, amount):
        raise HTTPException(status_code=400, detail="Insufficient balance")
    else:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status() # Check that the request was successful

        # deduct money from wallet
        withdraw_req = deduct_amount_from_wallet(db, user.id, amount)

        # create transaction log
        paypal_transaction_id = response.json().get("batch_header").get("payout_batch_id")
        withdraw_entry = create_withdraw_transaction(db, user.id, amount, paypal_transaction_id)

        return {"status": "success", "updated_balance": withdraw_req.balance, "email": account_email, "withdraw": withdraw_entry}
