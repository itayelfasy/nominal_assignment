"""Authentication routes for QuickBooks integration."""
import logging
from typing import Dict

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.token_service import TokenService
from app.services.quickbooks_service import QuickBooksService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])

@router.get("/quickbooks")
async def quickbooks_auth() -> Dict[str, str]:
    """Initiate OAuth flow with QuickBooks.
    
    Returns:
        Dict[str, str]: Authorization URL for QuickBooks OAuth.
    """
    auth_url = await QuickBooksService.get_authorization_url()
    return {"auth_url": auth_url}

@router.get("/callback")
async def quickbooks_callback(
    code: str,
    realm_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Handle OAuth callback from QuickBooks.
    
    Args:
        code: Authorization code from QuickBooks.
        realm_id: QuickBooks company realm ID.
        db: Database session.
        
    Returns:
        Dict[str, str]: Authentication result with tokens.
        
    Raises:
        HTTPException: If authentication fails.
    """
    try:
        logger.info("\n=== QuickBooks OAuth Callback ===")
        logger.info(f"Received Realm ID: {realm_id}")
        logger.info(f"Received Auth Code: {code}")
        logger.info("===============================\n")

        return await TokenService.handle_callback(code, realm_id, db)
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}") 