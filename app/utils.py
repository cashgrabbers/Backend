## utils.py
from sqlalchemy import or_
from typing import Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User, Wallet, Transaction
from schemas import UserCreate, WalletCreate, TransactionCreate, UserWithWallet, WalletOut
from auth import hash_password

def get_user(db: Session, user_id: int) -> Any:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Any:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    # check if email already registered
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    
    # create user
    db_user = User(email=user.email, password=hashed_password, first_name=user.first_name, last_name=user.last_name, phone_number=user.phone_number)
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

def get_wallets(db: Session, skip: int = 0, limit: int = 100) -> List[Wallet]:
    return db.query(Wallet).offset(skip).limit(limit).all()

# def create_wallet(db: Session, wallet: WalletCreate, user_id: int) -> Wallet:
#     db_wallet = Wallet(**wallet.dict(), user_id=user_id)
#     db.add(db_wallet)
#     db.commit()
#     db.refresh(db_wallet)
#     return db_wallet

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
            currency=orm_user.wallet.currency
        ),
    )

def transfer_money(db: Session, transaction: TransactionCreate, current_user: User) -> Transaction:
    # Fetch sender's wallet
    sender_wallet = db.query(Wallet).filter(Wallet.id == transaction.sender_wallet_id).first()

    # Ensure the authenticated user is the owner of the sender's wallet
    if sender_wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to make transactions from this wallet")
    
    sender_wallet = db.query(Wallet).filter(Wallet.id == transaction.sender_wallet_id).first()
    receiver_wallet = db.query(Wallet).filter(Wallet.id == transaction.receiver_wallet_id).first()

    if not sender_wallet or not receiver_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if sender_wallet.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Perform the transaction
    sender_wallet.balance -= transaction.amount
    receiver_wallet.balance += transaction.amount

    # Log the transaction
    db_transaction = Transaction(
        sender_wallet_id=transaction.sender_wallet_id, 
        receiver_wallet_id=transaction.receiver_wallet_id, 
        amount=transaction.amount
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction

# def get_transaction(db: Session, transaction_id: int) -> Any:
#     return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_transactions(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[Transaction]:
    return db.query(Transaction) \
            .filter(or_(Transaction.sender_wallet_id == current_user.id, Transaction.receiver_wallet_id == current_user.id)) \
            .offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

