from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta

from ..config import settings
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import (
    UserCreate,
    User,
    Token,
    WalletCreate,
    Wallet,
    TransactionCreate,
    Transaction,
    UserWithWallet,
    TransactionOut,
)
from ..auth import authenticate_user, create_access_token, get_current_user
from ..utils import (
    get_user,
    get_users,
    create_user,
    get_wallet,
    get_wallets,
    # get_transaction,
    get_transactions,
    create_transaction,
    check_wallet_balance,
    update_wallet_balance,
    to_user_with_wallet,
    transfer_money,
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


@router.get("/users", response_model=UserWithWallet)
def get_protected_route(current_user: User = Depends(get_current_user)):
    return to_user_with_wallet(current_user)

@router.post("/transfer", response_model=Transaction)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    # verify JWT token and get current user
    current_user: User = Depends(get_current_user),
):
    return transfer_money(db=db, transaction=transaction, current_user=current_user)


@router.get("/transactions", response_model=List[TransactionOut])
def get_all_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get all transactions. Can be filtered with optional skip and limit parameters.
    """
    transactions = get_transactions(db, current_user = current_user, skip=skip, limit=limit)
    return transactions
