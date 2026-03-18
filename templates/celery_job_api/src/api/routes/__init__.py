from fastapi import APIRouter

from api.routes.base_routes import router as base_router

router = APIRouter()
router.include_router(base_router)

# Modules can append additional include_router(...) blocks here.

