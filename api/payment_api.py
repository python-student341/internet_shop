from fastapi import APIRouter, HTTPException, Cookie
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from schemas.payment_schema import PayItemSchema
from models.models import UserModel, CartItemModel, CartModel, CardModel
from database.database import session_dep
from database.hash import security


router = APIRouter()


@router.put('/payment/pay_for_one_item', tags=['Payment'])
async def pay_one_item(data: PayItemSchema, session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = await session.execute(select(UserModel).where(UserModel.id == user_id))
    current_user = query.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    query_current_item = await session.execute(select(CartItemModel).where(CartItemModel.id == data.cart_item_id).options(joinedload(CartItemModel.product)))
    current_item = query_current_item.scalar_one_or_none()

    if not current_item:
        raise HTTPException(status_code=404, detail='There is no such product in your cart')

    query_current_card = await session.execute(select(CardModel).where(CardModel.user_id == user_id))
    current_card = query_current_card.scalar_one_or_none()

    if not current_card:
        raise HTTPException(status_code=404, detail='Card not found')

    final_price = current_item.product.price * current_item.quantity

    if current_card.balance < final_price:
        raise HTTPException(status_code=400, detail='Not enough balance on your card')

    current_card.balance -= final_price

    await session.delete(current_item)
    await session.commit()

    return {'success': True, 'message': f'Paid {final_price} for the product'}


@router.put('/payment/pay_for_all_items', tags=['Payment'])
async def pay_all_items(session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = await session.execute(select(UserModel).where(UserModel.id == user_id))
    current_user = query.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    query_current_user_cart = await session.execute(select(CartModel).where(CartModel.user_id == user_id))
    current_user_cart = query_current_user_cart.scalar_one_or_none()

    query_current_items = await session.execute(select(CartItemModel).where(CartItemModel.cart_id == current_user_cart.id))
    current_items = query_current_items.scalars().all()

    if not current_items:
        raise HTTPException(status_code=404, detail='Your cart is empty')

    query_current_card = await session.execute(select(CardModel).where(CardModel.user_id == user_id))
    current_card = query_current_card.scalar_one_or_none()

    if not current_card:
        raise HTTPException(status_code=404, detail='Card not found')

    final_price = current_user_cart.total_price

    if current_card.balance < final_price:
        raise HTTPException(status_code=400, detail='Not enough balance on your card')

    current_card.balance -= final_price

    for item in current_items:
        await session.delete(item)

    current_user_cart.total_price = 0

    await session.commit()

    return {'success': True, 'message': f'Paid {final_price} for the product'}