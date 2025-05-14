"""QuickBooks API client implementation."""
import requests
import time
from app.core.config import get_settings
from app.core.constants import (
    QUICKBOOKS_API_VERSION,
    QUICKBOOKS_QUERY_ENDPOINT,
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_TEXT,
    AUTHORIZATION_BEARER,
    ERROR_UNAUTHORIZED,
    ERROR_BAD_REQUEST,
    ERROR_FORBIDDEN,
    ERROR_EMPTY_RESPONSE,
    ERROR_JSON_PARSE,
    ERROR_API_COMMUNICATION,
    ERROR_RATE_LIMIT,
    ERROR_SERVER_ERROR,
    LOG_API_REQUEST,
    LOG_API_RESPONSE,
    LOG_JSON_ERROR,
    LOG_REQUEST_ERROR,
    LOG_RATE_LIMIT,
    OAUTH_CLIENT_ID,
    OAUTH_RESPONSE_TYPE,
    OAUTH_CODE,
    OAUTH_SCOPE,
    OAUTH_REDIRECT_URI,
    OAUTH_STATE,
    OAUTH_REALM_ID,
    OAUTH_MINOR_VERSION,
    OAUTH_GRANT_TYPE,
    OAUTH_AUTHORIZATION_CODE,
    OAUTH_REFRESH_TOKEN,
    SQL_SELECT_ALL_ACCOUNTS,
    SQL_WHERE_NAME_LIKE,
    RESPONSE_QUERY,
    RESPONSE_ACCOUNT,
    RESPONSE_ERROR,
    RATE_LIMIT_MAX_RETRIES,
    RATE_LIMIT_RETRY_DELAY,
    RATE_LIMIT_HEADER
)
from app.models import Token
import json
from typing import Optional, Dict, Any, Tuple
import logging
from urllib.parse import urljoin

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuickBooksService:
    """Service for interacting with the QuickBooks API."""

    def __init__(self) -> None:
        """Initialize QuickBooks service with configuration from settings."""
        self.client_id = settings.QUICKBOOKS_CLIENT_ID
        self.client_secret = settings.QUICKBOOKS_CLIENT_SECRET
        self.redirect_uri = settings.QUICKBOOKS_REDIRECT_URI
        self.base_url = settings.QUICKBOOKS_SANDBOX_URL
        self.auth_url = settings.QUICKBOOKS_AUTH_URL
        self.token_url = settings.QUICKBOOKS_TOKEN_URL
        self.scope = settings.QUICKBOOKS_SCOPE
        self.state = settings.QUICKBOOKS_STATE
        self.sandbox_realm_id = settings.QUICKBOOKS_SANDBOX_REALM_ID

    @staticmethod
    def _handle_rate_limit(response: requests.Response) -> Tuple[bool, Optional[int]]:
        """Handle rate limit response from QuickBooks API.
        
        Args:
            response: The response from the API.
            
        Returns:
            Tuple[bool, Optional[int]]: (should_retry, retry_after_seconds)
        """
        if response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get(RATE_LIMIT_HEADER, RATE_LIMIT_RETRY_DELAY))
            logger.warning(LOG_RATE_LIMIT.format(retry_after=retry_after))
            return True, retry_after
        return False, None

    @staticmethod
    def _make_request(method: str, url: str, **kwargs) -> requests.Response:
        """Make an HTTP request with retry logic for rate limits.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to make the request to
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            requests.Response: The response from the API
            
        Raises:
            ValueError: If the request fails after all retries
        """
        retries = 0
        while retries < RATE_LIMIT_MAX_RETRIES:
            try:
                response = requests.request(method, url, **kwargs)
                
                # Check for rate limit
                should_retry, retry_after = QuickBooksService._handle_rate_limit(response)
                if should_retry:
                    time.sleep(retry_after)
                    retries += 1
                    continue
                
                # Handle other error status codes
                if response.status_code >= 500:
                    raise ValueError(ERROR_SERVER_ERROR.format(status_code=response.status_code))
                
                return response
                
            except requests.exceptions.RequestException as e:
                if retries == RATE_LIMIT_MAX_RETRIES - 1:
                    raise ValueError(ERROR_API_COMMUNICATION.format(error=str(e)))
                retries += 1
                time.sleep(RATE_LIMIT_RETRY_DELAY)
        
        raise ValueError(ERROR_RATE_LIMIT.format(retry_after=RATE_LIMIT_RETRY_DELAY))

    @classmethod
    async def get_authorization_url(cls) -> str:
        """Generate the authorization URL for OAuth flow.
        
        Returns:
            str: Complete authorization URL for QuickBooks OAuth.
        """
        service = cls()
        params = {
            OAUTH_CLIENT_ID: service.client_id,
            OAUTH_RESPONSE_TYPE: OAUTH_CODE,
            OAUTH_SCOPE: service.scope,
            OAUTH_REDIRECT_URI: service.redirect_uri,
            OAUTH_STATE: service.state,
            OAUTH_REALM_ID: service.sandbox_realm_id,
            OAUTH_MINOR_VERSION: QUICKBOOKS_API_VERSION
        }
        return f"{service.auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    @classmethod
    async def get_tokens(cls, auth_code: str) -> Token:
        """Exchange authorization code for access and refresh tokens.
        
        Args:
            auth_code: Authorization code received from QuickBooks.
            
        Returns:
            Token: Access and refresh tokens.
            
        Raises:
            ValueError: If token exchange fails.
        """
        service = cls()
        data = {
            OAUTH_GRANT_TYPE: OAUTH_AUTHORIZATION_CODE,
            OAUTH_CODE: auth_code,
            OAUTH_REDIRECT_URI: service.redirect_uri
        }
        response = cls._make_request(
            "POST",
            service.token_url,
            data=data,
            auth=(service.client_id, service.client_secret)
        )
        response.raise_for_status()
        return Token(**response.json())

    @classmethod
    async def refresh_tokens(cls, refresh_token: str) -> Token:
        """Refresh the access token using the refresh token.
        
        Args:
            refresh_token: Current refresh token.
            
        Returns:
            Token: New access and refresh tokens.
            
        Raises:
            ValueError: If token refresh fails.
        """
        service = cls()
        data = {
            OAUTH_GRANT_TYPE: OAUTH_REFRESH_TOKEN,
            OAUTH_REFRESH_TOKEN: refresh_token
        }
        response = cls._make_request(
            "POST",
            service.token_url,
            data=data,
            auth=(service.client_id, service.client_secret)
        )
        response.raise_for_status()
        return Token(**response.json())

    @classmethod
    async def get_accounts(cls, access_token: str, realm_id: str, name_prefix: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve accounts from QuickBooks.
        
        Args:
            access_token: Valid QuickBooks access token.
            realm_id: QuickBooks company realm ID.
            name_prefix: Optional filter for account names.
            
        Returns:
            Dict[str, Any]: QuickBooks accounts data.
            
        Raises:
            ValueError: If the API request fails or returns invalid data.
        """
        service = cls()
        headers = {
            "Authorization": AUTHORIZATION_BEARER.format(token=access_token),
            "Accept": CONTENT_TYPE_JSON,
            "Content-Type": CONTENT_TYPE_TEXT
        }

        query = SQL_SELECT_ALL_ACCOUNTS
        if name_prefix:
            query += SQL_WHERE_NAME_LIKE.format(name_prefix=name_prefix)

        url = urljoin(service.base_url, QUICKBOOKS_QUERY_ENDPOINT.format(realm_id=realm_id))

        try:
            logger.info(LOG_API_REQUEST)
            logger.info(f"URL: {url}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Query: {query}")

            response = cls._make_request(
                "POST",
                url,
                headers=headers,
                data=query,
                params={OAUTH_MINOR_VERSION: QUICKBOOKS_API_VERSION}
            )

            logger.info(LOG_API_RESPONSE)
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Content: {response.text}")

            if response.status_code == 401:
                raise ValueError(ERROR_UNAUTHORIZED)
            elif response.status_code == 400:
                raise ValueError(ERROR_BAD_REQUEST.format(message=response.text))
            elif response.status_code == 403:
                raise ValueError(ERROR_FORBIDDEN)

            if not response.text.strip():
                logger.warning(ERROR_EMPTY_RESPONSE)
                return {RESPONSE_QUERY: {RESPONSE_ACCOUNT: []}}

            try:
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(LOG_JSON_ERROR.format(error=str(e)))
                raise ValueError(ERROR_JSON_PARSE.format(error=str(e)))

        except requests.exceptions.RequestException as e:
            logger.error(LOG_REQUEST_ERROR.format(error=str(e)))
            raise ValueError(ERROR_API_COMMUNICATION.format(error=str(e))) 