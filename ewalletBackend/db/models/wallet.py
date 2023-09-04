from ewalletBackend.db.base import Base
import datetime

class Wallet(Base):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime