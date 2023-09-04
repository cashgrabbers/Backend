## utils.py

from typing import Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ewalletBackend.db.models import User, Wallet, Transaction
from ewalletBackend.services.auth import hash_password, get_current_active_user

def get_user(db: Session, user_id: int) -> Any:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Any:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: User) -> User:
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, password=hashed_password, first_name=user.first_name, last_name=user.last_name, phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_wallet(db: Session, wallet_id: int) -> Any:
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()

def get_wallets(db: Session, skip: int = 0, limit: int = 100) -> List[Wallet]:
    return db.query(Wallet).offset(skip).limit(limit).all()

def create_wallet(db: Session, wallet: Wallet, user_id: int) -> Wallet:
    db_wallet = Wallet(**wallet.dict(), user_id=user_id)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def get_transaction(db: Session, transaction_id: int) -> Any:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[Transaction]:
    return db.query(Transaction).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: Transaction) -> Transaction:
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def check_wallet_balance(db: Session, wallet_id: int, amount: float) -> bool:
    wallet = get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if wallet.balance < amount:
        return False
    return True

def update_wallet_balance(db: Session, wallet_id: int, amount: float, transaction_type: str) -> Wallet:
    wallet = get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if transaction_type == "debit":
        if wallet.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        wallet.balance -= amount
    elif transaction_type == "credit":
        wallet.balance += amount
    db.commit()
    return wallet
