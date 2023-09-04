from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        orm_mode = True

class WalletBase(BaseModel):
    user_id: int

class WalletCreate(WalletBase):
    pass

class Currency(Enum):
    SGD = "SGD"
    USD = "USD"
    EUR = "EUR"

class Wallet(WalletBase):
    id: int
    balance: float
    currency: Currency = Currency.SGD
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    sender_wallet_id: int
    receiver_wallet_id: int
    amount: float

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None