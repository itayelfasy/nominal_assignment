import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router, auth_router

app = FastAPI(
    title="Nominal QuickBooks Integration",
    description="API for QuickBooks Online integration using OAuth 2.0",
    version="1.0.0",
    author="Itay Elfasy"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_router)  # No prefix for auth routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Nominal QuickBooks Integration API",
        "author": "Itay Elfasy",
        "endpoints": {
            "auth": "/auth/quickbooks",
            "callback": "/callback",
            "accounts": "/api/accounts"
        }
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
