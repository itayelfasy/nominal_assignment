"""Token service for managing QuickBooks authentication tokens."""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.models import QuickBooksToken, Token
from app.services.quickbooks_service import QuickBooksService

logger = logging.getLogger(__name__)

class TokenService:
    @staticmethod
    async def handle_callback(code: str, realm_id: str, db: Session) -> Dict[str, str]:
        """Handle OAuth callback and store tokens.
        
        Args:
            code: Authorization code from QuickBooks.
            realm_id: QuickBooks company realm ID.
            db: Database session.
            
        Returns:
            Dict[str, str]: Authentication result with tokens.
        """
        tokens = await QuickBooksService.get_tokens(code)
        return await TokenService.store_tokens(tokens, realm_id, db)

    @staticmethod
    async def store_tokens(tokens: Token, realm_id: str, db: Session) -> Dict[str, str]:
        """Store QuickBooks tokens in database.
        
        Args:
            tokens: QuickBooks tokens.
            realm_id: QuickBooks company realm ID.
            db: Database session.
            
        Returns:
            Dict[str, str]: Authentication result with tokens.
        """
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

    @staticmethod
    async def get_valid_token(realm_id: str, db: Session) -> Optional[str]:
        """Get a valid access token for the given realm ID.
        
        Args:
            realm_id: QuickBooks company realm ID.
            db: Database session.
            
        Returns:
            Optional[str]: Valid access token or None if not found.
        """
        db_token = db.query(QuickBooksToken).filter(QuickBooksToken.realm_id == realm_id).first()
        if not db_token:
            return None

        # Check if token is expired
        token_age = datetime.utcnow() - db_token.created_at
        if token_age > timedelta(seconds=db_token.expires_in):
            try:
                # Refresh token
                new_tokens = await QuickBooksService.refresh_tokens(db_token.refresh_token)

                # Update database
                db_token.access_token = new_tokens.access_token
                db_token.refresh_token = new_tokens.refresh_token
                db_token.token_type = new_tokens.token_type
                db_token.expires_in = new_tokens.expires_in
                db_token.x_refresh_token_expires_in = new_tokens.x_refresh_token_expires_in
                db_token.created_at = datetime.utcnow()
                db.commit()

                return new_tokens.access_token
            except Exception as e:
                logger.error(f"Token refresh failed: {str(e)}")
                return None

        return db_token.access_token 