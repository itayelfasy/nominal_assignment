"""Constants used throughout the application."""

# QuickBooks API Constants
QUICKBOOKS_API_VERSION = "75"
QUICKBOOKS_QUERY_ENDPOINT = "/v3/company/{realm_id}/query"

# HTTP Headers
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_TEXT = "application/text"
AUTHORIZATION_BEARER = "Bearer {token}"

# Error Messages
ERROR_UNAUTHORIZED = "Unauthorized: Token may be invalid or expired"
ERROR_BAD_REQUEST = "Bad Request: {message}"
ERROR_FORBIDDEN = "Forbidden: Application may not have the required permissions"
ERROR_EMPTY_RESPONSE = "Received empty response from QuickBooks API"
ERROR_JSON_PARSE = "Invalid JSON response from QuickBooks API: {error}"
ERROR_API_COMMUNICATION = "Failed to communicate with QuickBooks API: {error}"
ERROR_RATE_LIMIT = "Rate limit exceeded. Please try again in {retry_after} seconds"
ERROR_SERVER_ERROR = "QuickBooks API server error: {status_code}"

# Log Messages
LOG_API_REQUEST = "\n=== QuickBooks API Request Details ==="
LOG_API_RESPONSE = "\n=== QuickBooks API Response Details ==="
LOG_JSON_ERROR = "\n=== JSON Parse Error Details ==="
LOG_REQUEST_ERROR = "\n=== Request Exception Details ==="
LOG_RATE_LIMIT = "Rate limit hit. Retrying after {retry_after} seconds"

# OAuth Parameters
OAUTH_CLIENT_ID = "client_id"
OAUTH_RESPONSE_TYPE = "response_type"
OAUTH_CODE = "code"
OAUTH_SCOPE = "scope"
OAUTH_REDIRECT_URI = "redirect_uri"
OAUTH_STATE = "state"
OAUTH_REALM_ID = "realmId"
OAUTH_MINOR_VERSION = "minorversion"
OAUTH_GRANT_TYPE = "grant_type"
OAUTH_AUTHORIZATION_CODE = "authorization_code"
OAUTH_REFRESH_TOKEN = "refresh_token"

# SQL Queries
SQL_SELECT_ALL_ACCOUNTS = "SELECT * FROM Account"
SQL_WHERE_NAME_LIKE = " WHERE Name LIKE '{name_prefix}%'"

# Response Keys
RESPONSE_QUERY = "QueryResponse"
RESPONSE_ACCOUNT = "Account"
RESPONSE_ERROR = "error"

# Rate Limiting
RATE_LIMIT_MAX_RETRIES = 3
RATE_LIMIT_RETRY_DELAY = 1  # seconds
RATE_LIMIT_HEADER = "Retry-After" 