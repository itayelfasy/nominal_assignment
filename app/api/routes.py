"""API routes for QuickBooks integration."""
from fastapi import APIRouter, HTTPException, Depends, Query
from app.api.quickbooks import quickbooks_client
from app.models.token import Token, TokenData
from app.models.database import QuickBooksToken
from app.core.database import get_db
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Create separate routers for API and auth
api_router = APIRouter(tags=["api"])
auth_router = APIRouter(tags=["auth"])

@auth_router.get("/quickbooks")
async def quickbooks_auth() -> Dict[str, str]:
    """Initiate OAuth flow with QuickBooks.
    
    Returns:
        Dict[str, str]: Authorization URL for QuickBooks OAuth.
    """
    auth_url = quickbooks_client.get_authorization_url()
    return {"auth_url": auth_url}

@auth_router.get("/callback")
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
        
        tokens = quickbooks_client.get_tokens(code)
        
        # Store tokens in database
        db_token = QuickBooksToken(
            realm_id=realm_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            x_refresh_token_expires_in=tokens.x_refresh_token_expires_in,
            created_at=datetime.utcnow()
        )
        
        # Update if exists, insert if not
        existing_token = db.query(QuickBooksToken).filter(QuickBooksToken.realm_id == realm_id).first()
        if existing_token:
            for key, value in db_token.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_token, key, value)
        else:
            db.add(db_token)
        
        db.commit()
        
        logger.info("\n=== QuickBooks Access Token ===")
        logger.info(f"Access Token: {tokens.access_token}")
        logger.info(f"Realm ID: {realm_id}")
        logger.info("=============================\n")
        
        return {
            "message": "Successfully authenticated with QuickBooks",
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "realm_id": realm_id
        }
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@api_router.get("/accounts")
async def get_accounts(
    realm_id: str,
    name_prefix: Optional[str] = Query(None, description="Filter accounts by name prefix"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Retrieve accounts from QuickBooks.
    
    Args:
        realm_id: QuickBooks company realm ID.
        name_prefix: Optional filter for account names.
        db: Database session.
        
    Returns:
        Dict[str, Any]: QuickBooks accounts data.
        
    Raises:
        HTTPException: If authentication fails or API request fails.
    """
    # Get token from database
    db_token = db.query(QuickBooksToken).filter(QuickBooksToken.realm_id == realm_id).first()
    if not db_token:
        raise HTTPException(
            status_code=401, 
            detail="Not authenticated with QuickBooks. Please visit /auth/quickbooks first."
        )
    
    # Check if token is expired
    token_age = datetime.utcnow() - db_token.created_at
    if token_age > timedelta(seconds=db_token.expires_in):
        try:
            # Refresh token
            new_tokens = quickbooks_client.refresh_tokens(db_token.refresh_token)
            
            # Update database
            db_token.access_token = new_tokens.access_token
            db_token.refresh_token = new_tokens.refresh_token
            db_token.token_type = new_tokens.token_type
            db_token.expires_in = new_tokens.expires_in
            db_token.x_refresh_token_expires_in = new_tokens.x_refresh_token_expires_in
            db_token.created_at = datetime.utcnow()
            db.commit()
            
            access_token = new_tokens.access_token
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Token refresh failed: {str(e)}"
            )
    else:
        access_token = db_token.access_token
    
    try:
        accounts = quickbooks_client.get_accounts(
            access_token,
            realm_id,
            name_prefix
        )
        return accounts
    except ValueError as e:
        logger.error(f"Error getting accounts: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Export both routers
router = APIRouter()
router.include_router(api_router)
router.include_router(auth_router) 