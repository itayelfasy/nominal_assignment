"""Account routes for QuickBooks integration."""
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.services.account_service import AccountService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["accounts"])
settings = get_settings()

@router.get("/accounts")
async def get_accounts(
    realm_id: str = Query(
        default=settings.QUICKBOOKS_SANDBOX_REALM_ID,
        description="QuickBooks company realm ID (defaults to sandbox realm ID)"
    ),
    name_prefix: Optional[str] = Query(None, description="Filter accounts by name prefix"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Retrieve accounts from QuickBooks.
    
    Args:
        realm_id: QuickBooks company realm ID (defaults to sandbox realm ID).
        name_prefix: Optional filter for account names.
        db: Database session.
        
    Returns:
        Dict[str, Any]: QuickBooks accounts data.
        
    Raises:
        HTTPException: If authentication fails or API request fails.
    """
    try:
        return await AccountService.get_accounts(realm_id, name_prefix, db)
    except ValueError as e:
        logger.error(f"Error getting accounts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 