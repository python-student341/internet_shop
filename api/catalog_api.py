from fastapi import APIRouter
from sqlalchemy import select

from database.database import session_dep
from models.models import CategoryModel, ProductModel


router = APIRouter()


@router.get('/category/get_category', tags=['Catalog'])
async def get_categories(session: session_dep):
    all_categories = await session.execute(select(CategoryModel))
    return all_categories.scalars().all()


@router.get('/category/product/get_products', tags=['Catalog'])
async def get_products(session: session_dep):
    all_products = await session.execute(select(ProductModel))
    return all_products.scalars().all()