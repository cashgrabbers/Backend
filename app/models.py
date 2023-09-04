## models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    wallet = relationship("Wallet", back_populates="user")

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="wallet")
    sent_transactions = relationship("Transaction", backref="sender_wallet", foreign_keys="[Transaction.sender_wallet_id]")
    received_transactions = relationship("Transaction", backref="receiver_wallet", foreign_keys="[Transaction.receiver_wallet_id]")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_wallet_id = Column(Integer, ForeignKey("wallets.id"))
    receiver_wallet_id = Column(Integer, ForeignKey("wallets.id"))
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
