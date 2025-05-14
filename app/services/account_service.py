"""Account service for managing QuickBooks accounts."""
import logging
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.services.token_service import TokenService
from app.services.quickbooks_service import QuickBooksService

logger = logging.getLogger(__name__)

class AccountService:
    @staticmethod
    async def get_accounts(
        realm_id: str,
        name_prefix: Optional[str],
        db: Session
    ) -> Dict[str, Any]:
        """Get accounts from QuickBooks.
        
        Args:
            realm_id: QuickBooks company realm ID.
            name_prefix: Optional filter for account names.
            db: Database session.
            
        Returns:
            Dict[str, Any]: QuickBooks accounts data.
            
        Raises:
            ValueError: If not authenticated or API request fails.
        """
        access_token = await TokenService.get_valid_token(realm_id, db)
        if not access_token:
            raise ValueError("Not authenticated with QuickBooks. Please visit /auth/quickbooks first.")

        try:
            return await QuickBooksService.get_accounts(
                access_token,
                realm_id,
                name_prefix
            )
        except Exception as e:
            logger.error(f"Error getting accounts: {str(e)}")
            raise ValueError(str(e)) 