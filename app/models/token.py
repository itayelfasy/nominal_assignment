from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    x_refresh_token_expires_in: int
    created_at: Optional[datetime] = None
    realm_id: Optional[str] = None

class TokenData(BaseModel):
    realm_id: Optional[str] = None 