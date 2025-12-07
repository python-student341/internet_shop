from fastapi import APIRouter

from backend.api.user_api import router as user_router
from backend.api.card_api import router as card_router
from backend.api.api_for_admin import router as admin_router
from backend.api.catalog_api import router as catalog_router
from backend.api.cart_api import router as cart_router
from backend.api.payment_api import router as payment_router

main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(card_router)
main_router.include_router(admin_router)
main_router.include_router(catalog_router)
main_router.include_router(cart_router)
main_router.include_router(payment_router)