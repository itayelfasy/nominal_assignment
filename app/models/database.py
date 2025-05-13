from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base
from datetime import datetime

class QuickBooksToken(Base):
    __tablename__ = "quickbooks_tokens"

    realm_id = Column(String, primary_key=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    token_type = Column(String, nullable=False)
    expires_in = Column(Integer, nullable=False)
    x_refresh_token_expires_in = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 