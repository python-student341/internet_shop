from fastapi import APIRouter

from api.user_api import router as user_router
from api.card_api import router as card_router
from api.api_for_admin import router as admin_router
from api.catalog_api import router as catalog_router
from api.cart_api import router as cart_router
from api.payment_api import router as payment_router

main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(card_router)
main_router.include_router(admin_router)
main_router.include_router(catalog_router)
main_router.include_router(cart_router)
main_router.include_router(payment_router)