from ewalletBackend.db.base import Base
import datetime

class Transaction(Base):
    id: int
    sender_wallet_id: int
    receiver_wallet_id: int
    amount: float
    created_at: datetime