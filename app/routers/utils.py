## utils.py
from typing import Any, List, Union

import requests
from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .auth import hash_password
from ..config import settings
from ..models import Transaction, User, Wallet, Deposit, Withdraw
from ..schemas import (
    TransactionCreate,
    UserCreate,
    UserWithWallet,
    WalletOut,
    DepositCreate,
)


def get_user(db: Session, user_id: int) -> Any:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    # check if email already registered
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)

    # create user
    db_user = User(
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
    )
    db.add(db_user)
    db.commit()

    # wallet is created
    db_wallet = Wallet(user_id=db_user.id, balance=100.0, currency="SGD")
    db.add(db_wallet)
    db.commit()

    db.refresh(db_user)
    db.refresh(db_wallet)
    return db_user


def get_wallet(db: Session, wallet_id: int) -> Any:
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()


def get_wallet_balance(db: Session, wallet_id: int) -> float:
    wallet = get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet.balance


def check_wallet_balance(db: Session, wallet_id: int, amount: float) -> bool:
    wallet = get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if wallet.balance < amount:
        return False
    return True


def to_user_with_wallet(orm_user: User) -> UserWithWallet:
    return UserWithWallet(
        id=orm_user.id,
        email=orm_user.email,
        first_name=orm_user.first_name,
        last_name=orm_user.last_name,
        phone_number=orm_user.phone_number,
        is_active=orm_user.is_active,
        is_superuser=orm_user.is_superuser,
        created_at=orm_user.created_at,
        updated_at=orm_user.updated_at,
        wallet=WalletOut(
            id=orm_user.wallet.id,
            balance=orm_user.wallet.balance,
            currency=orm_user.wallet.currency,
        ),
    )


def transfer_money(
    db: Session, transaction: TransactionCreate, current_user: User
) -> Transaction:
    # Get receiver email
    receiver_email = transaction.receiver_wallet_email

    # From receiver email, get receiver user object
    receiver_user = get_user_by_email(db, receiver_email)

    if not receiver_user:
        raise HTTPException(status_code=404, detail="No such email on app")

    # From receiver user object, get receiver wallet
    receiver_wallet = get_wallet(db, receiver_user.id)

    # Fetch sender's wallet using the current user's ID
    sender_wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()

    if not sender_wallet:
        raise HTTPException(status_code=404, detail="Sender's wallet not found")

    if not receiver_wallet:
        raise HTTPException(status_code=404, detail="Receiver's wallet not found")

    if sender_wallet.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Perform the transaction
    sender_wallet.balance -= transaction.amount
    receiver_wallet.balance += transaction.amount

    # Log the transaction
    db_transaction = Transaction(
        sender_wallet_id=sender_wallet.id,  # Use sender_wallet.id directly here
        receiver_wallet_id=receiver_wallet.id,
        amount=transaction.amount,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    print(db_transaction)

    return db_transaction


# def get_transaction(db: Session, transaction_id: int) -> Any:
#     return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_transactions_and_deposits(
    db: Session, current_user: User, skip: int = 0, limit: int = 100
) -> List[Union[Transaction, Deposit, Withdraw]]:
    # trasnactions
    transactions = (
        db.query(Transaction)
        .filter(
            or_(
                Transaction.sender_wallet_id == current_user.id,
                Transaction.receiver_wallet_id == current_user.id,
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    # deposits
    deposits = (
        db.query(Deposit)
        .filter(Deposit.receiver_wallet_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    # withdrawals
    withdrawals = (
        db.query(Withdraw)
        .filter(Withdraw.sender_wallet_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Combine transactions, deposits, and withdrawals
    combined = (
        [{"item_type": "transaction", "data": t} for t in transactions]
        + [{"item_type": "deposit", "data": d} for d in deposits]
        + [{"item_type": "withdrawal", "data": w} for w in withdrawals]
    )

    return sorted(combined, key=lambda k: k["data"].created_at, reverse=True)


def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def add_balance_to_wallet(db: Session, wallet_id: int, amount: float):
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet.balance += amount
    db.commit()
    return wallet


def deduct_amount_from_wallet(db: Session, wallet_id: int, amount: float) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    wallet.balance -= amount
    db.commit()
    return wallet


def get_paypal_session():
    try:
        url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

        payload = "grant_type=client_credentials"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + settings.PAYPAL_API_KEY,
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


def create_deposit_transaction(db: Session, deposit: DepositCreate):
    db_deposit = Deposit(**deposit.dict())
    db.add(db_deposit)
    db.commit()
    db.refresh(db_deposit)
    return db_deposit


def create_withdraw_transaction(
    db: Session, user_id: int, amount: float, paypal_transaction_id: str
):
    db_withdraw = Withdraw(
        sender_wallet_id=user_id,
        amount=amount,
        currency="SGD",
        paypal_payout_id=paypal_transaction_id,
    )
    db.add(db_withdraw)
    db.commit()
    db.refresh(db_withdraw)
    return db_withdraw
