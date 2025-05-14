"""Main application module."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

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
app.include_router(router)

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
