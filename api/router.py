from fastapi import APIRouter

from api.user_api import router as user_router
from api.card_api import router as card_router
from api.api_for_admin import router as admin_router

main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(card_router)
main_router.include_router(admin_router)