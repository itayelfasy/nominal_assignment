# Nominal QuickBooks Integration

API for integrating with QuickBooks Online using OAuth 2.0 authentication.

## Prerequisites

- Docker and Docker Compose installed
- QuickBooks Developer account
- QuickBooks API credentials (Client ID and Client Secret)

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd nominal
```

2. Create a `.env` file in the root directory with your QuickBooks credentials:

```env
QUICKBOOKS_CLIENT_ID=your_client_id
QUICKBOOKS_CLIENT_SECRET=your_client_secret
QUICKBOOKS_REDIRECT_URI=your_redirect_uri
QUICKBOOKS_SANDBOX_URL=your_sandbox_url
QUICKBOOKS_AUTH_URL=your_auth_url
QUICKBOOKS_TOKEN_URL=your_token_url
QUICKBOOKS_SCOPE=com.intuit.quickbooks.accounting
QUICKBOOKS_STATE=random_state
QUICKBOOKS_SANDBOX_REALM_ID=your_sandbox_realm_id
```

3. Start the application using Docker Compose:

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8080`

## API Flow

### 1. Authentication Flow

1. **Initiate OAuth**:

   - Visit: `http://localhost:8080/auth/quickbooks`
   - This will redirect you to QuickBooks login page
   - After logging in, QuickBooks will redirect back to your callback URL

2. **Handle Callback**:
   - The callback URL will receive the authorization code
   - The application will exchange it for access and refresh tokens
   - Tokens are stored in the database for future use

### 2. Accessing QuickBooks Data

1. **Get Accounts**:
   - Endpoint: `GET http://localhost:8080/api/accounts?realm_id=YOUR_REALM_ID`
   - Optional: Add `name_prefix` parameter to filter accounts
   - Example: `http://localhost:8080/api/accounts?realm_id=YOUR_REALM_ID&name_prefix=Bank`

### Important Notes

- The application uses PostgreSQL for token storage
- Data is persisted using Docker volumes
- The database is automatically initialized on first run
- Tokens are automatically refreshed when expired

## Development

- The application uses FastAPI for the backend
- SQLAlchemy for database operations
- Docker for containerization
- PostgreSQL for data storage

## API Documentation

Once the application is running, you can access:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Stopping the Application

To stop the application:

```bash
docker-compose down
```

To stop and remove all data (including the database volume):

```bash
docker-compose down -v
```

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── quickbooks.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── token.py
│   └── main.py
├── .env
├── requirements.txt
└── README.md
```

## Setup and Installation

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

- Copy `.env.example` to `.env`
- Fill in your QuickBooks credentials

4. Run the application:

```bash
uvicorn app.main:app --reload
```

## API Endpoints

### OAuth Flow

- `GET /auth/quickbooks`: Initiates the OAuth flow with QuickBooks
- `GET /callback`: Handles the OAuth callback from QuickBooks

### Accounts

- `GET /api/accounts`: Retrieves all accounts
- `GET /api/accounts?name_prefix={prefix}`: Retrieves accounts filtered by name prefix

## Testing

The API can be tested using tools like Postman or curl. Example:

```bash
# Get all accounts
curl http://localhost:8080/api/accounts

# Get accounts with name prefix
curl http://localhost:8080/api/accounts?name_prefix=Bank
```

## Author

Itay Elfasy
