from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Union

'''
Users
'''
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
        
'''
Logins
'''
class LoginRequest(BaseModel):
    email: str
    password: str

'''
Wallets
'''
class Currency(Enum):
    SGD = "SGD"
    USD = "USD"
    EUR = "EUR"

class WalletOut(BaseModel):
    id: int
    balance: float
    currency: Currency = Currency.SGD
    
class UserWithWallet(User):
    wallet: WalletOut

class WalletBase(BaseModel):
    user_id: int

class WalletCreate(WalletBase):
    pass

class Wallet(WalletBase):
    id: int
    balance: float
    currency: Currency = Currency.SGD
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        orm_mode = True

'''
Transactions
'''
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

class TransactionOut(BaseModel):
    id: int
    sender_wallet_id: int
    receiver_wallet_id: int
    amount: float
    created_at: datetime

    class Config:
        orm_mode = True

class DepositOut(BaseModel):
    id: int
    receiver_wallet_id: int
    amount: float
    created_at: datetime

    class Config:
        orm_mode = True

class TransactionAndDepositOut(BaseModel):
    item_type: str
    data: Union[TransactionOut, DepositOut]


'''
Tokens
'''
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    
# TODO: Add in withdraws and deposits

'''
Deposits
'''
class DepositRequest(BaseModel):
    amount: float
    
class CaptureRequest(BaseModel):
    deposit_id: str
    
    
class DepositBase(BaseModel):
    receiver_wallet_id: int
    amount: float
    currency: str
    paypal_order_id: str

class DepositCreate(DepositBase):
    pass

class Deposit(DepositBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True