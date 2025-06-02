from fastapi import APIRouter

from app.auth.routes import router as auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
