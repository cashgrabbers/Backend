## exceptions.py
from fastapi import HTTPException

class InsufficientBalanceException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Insufficient balance in the wallet")

class WalletNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Wallet not found")

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")

class TransactionNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Transaction not found")
