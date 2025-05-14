"""API routes package."""
from fastapi import APIRouter
from app.api.routes import auth, accounts

# Export both routers
router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(accounts.router, prefix="/accounts", tags=["accounts"]) 