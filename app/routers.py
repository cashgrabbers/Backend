from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta

from config import settings
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import (
    UserCreate,
    User,
    Token,
    WalletCreate,
    Wallet,
    TransactionCreate,
    Transaction,
)
from auth import authenticate_user, create_access_token, get_current_user
from utils import (
    get_user,
    get_users,
    create_user,
    get_wallet,
    get_wallets,
    create_wallet,
    get_transaction,
    get_transactions,
    create_transaction,
    check_wallet_balance,
    update_wallet_balance,
)

router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.post("/create", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires,
    )

    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})


@router.get("/users", response_model=User)
def get_protected_route(current_user: User = Depends(get_current_user)):
    return current_user



# @router.get("/users", response_model=List[User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = get_users(db, skip=skip, limit=limit)
#     return users

# @router.get("/users/{user_id}", response_model=User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

# @router.post("/wallets", response_model=Wallet, status_code=status.HTTP_201_CREATED)
# def create_wallet_route(wallet: WalletCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
#     return create_wallet(db=db, wallet=wallet, user_id=current_user.id)

# @router.get("/wallets", response_model=List[Wallet])
# def read_wallets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     wallets = get_wallets(db, skip=skip, limit=limit)
#     return wallets

# @router.get("/wallets/{wallet_id}", response_model=Wallet)
# def read_wallet(wallet_id: int, db: Session = Depends(get_db)):
#     db_wallet = get_wallet(db, wallet_id=wallet_id)
#     if db_wallet is None:
#         raise HTTPException(status_code=404, detail="Wallet not found")
#     return db_wallet

# @router.post("/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
# def create_transaction_route(transaction: TransactionCreate, db: Session = Depends(get_db)):
#     if not check_wallet_balance(db, transaction.sender_wallet_id, transaction.amount):
#         raise HTTPException(status_code=400, detail="Insufficient balance")
#     db_transaction = create_transaction(db=db, transaction=transaction)
#     update_wallet_balance(db, transaction.sender_wallet_id, transaction.amount, "debit")
#     update_wallet_balance(db, transaction.receiver_wallet_id, transaction.amount, "credit")
#     return db_transaction

# @router.get("/transactions", response_model=List[Transaction])
# def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     transactions = get_transactions(db, skip=skip, limit=limit)
#     return transactions

# @router.get("/transactions/{transaction_id}", response_model=Transaction)
# def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
#     db_transaction = get_transaction(db, transaction_id=transaction_id)
#     if db_transaction is None:
#         raise HTTPException(status_code=404, detail="Transaction not found")
#     return db_transaction
