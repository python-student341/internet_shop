from fastapi import APIRouter, HTTPException, Cookie
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload

from backend.models.models import CartItemModel, CartModel, UserModel, ProductModel
from backend.schemas.cart_schema import CartItemSchema, DeleteItemSchema, DeleteOneItemSchema
from backend.database.database import session_dep
from backend.database.hash import security


router = APIRouter()


@router.post('/cart/add_product_to_cart', tags=['Cart'])
async def add_product(data: CartItemSchema, session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = security._decode_token(token)
    user_id = int(payload.sub)

#   Get current user
    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

#   Get current product from catalog to add in the cart
    product_query = select(ProductModel).where(ProductModel.id == data.product_id)
    product_result = await session.execute(product_query)
    current_product = product_result.scalar_one_or_none()

#   Get cart for the current user
    query_cart = select(CartModel).where(CartModel.user_id == user_id)
    cart_result = await session.execute(query_cart)
    current_cart = cart_result.scalar_one_or_none()

    if not current_product:
        raise HTTPException(status_code=404, detail='Product not found')

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

#   We check the availability of the product being added in the cart
    query_item = select(CartItemModel).where(CartItemModel.product_id == data.product_id, CartItemModel.cart_id == current_cart.id)
    result_item = await session.execute(query_item)
    current_item = result_item.scalar_one_or_none()

    if current_item:
        current_item.quantity += data.quantity
        current_cart.total_price += current_product.price * data.quantity
        await session.commit()
        await session.refresh(current_cart)
    else:
#   Add new product in the cart
        new_item = CartItemModel(
            cart_id=current_cart.id,
            product_id=data.product_id,
            quantity=data.quantity
        )

        session.add(new_item)

        current_cart.total_price += current_product.price * data.quantity

        await session.commit()
        await session.refresh(current_cart)

    return {'success': True, 'message': 'Product was added'}


@router.get('/cart/get_info', tags=['Cart'])
async def get_info(session: session_dep, token: str = Cookie):
    
    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query_user_cart = select(CartModel).where(CartModel.user_id == user_id)
    result_user_cart = await session.execute(query_user_cart)
    current_user_cart = result_user_cart.scalar_one_or_none()

    query_cart_items = (select(CartItemModel).where(CartItemModel.cart_id == current_user_cart.id).options(joinedload(CartItemModel.product)))
    result_cart_items = await session.execute(query_cart_items)
    cart_items = result_cart_items.scalars().all()

    # Формируем ответ
    return {
        'cart_items': [{
            'product_id': item.product_id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'total': item.product.price * item.quantity
        } for item in cart_items],
        'total_price': current_user_cart.total_price
    }


@router.put('/cart/remove_one_item', tags=['Cart'])
async def remove_one_item(data: DeleteOneItemSchema, session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    query_item = select(CartItemModel).where(CartItemModel.id == data.cart_item_id)
    result_item = await session.execute(query_item)
    current_item = result_item.scalar_one_or_none()

    if not current_item:
        raise HTTPException(status_code=404, detail='There is no such product in your cart')

    current_item.quantity -= data.amount

    if current_item.quantity <= 0:
        await session.delete(current_item)

    await session.commit()

    return {'success': True, 'message': 'Product quantity decreased'}


@router.delete('/cart/delete_product', tags=['Cart'])
async def delete_item(data: DeleteItemSchema, session: session_dep, token: str = Cookie):
    
    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    query_item = select(CartItemModel).where(CartItemModel.id == data.cart_item_id)
    result_item = await session.execute(query_item)
    current_item = result_item.scalar_one_or_none()

    if not current_item:
        raise HTTPException(status_code=404, detail='There is no such product in your cart')

    await session.delete(current_item)
    await session.commit()

    query_current_user_cart = await session.execute(select(CartModel).where(CartModel.user_id == user_id))
    current_user_cart = query_current_user_cart.scalar_one_or_none()

    query_items = select(CartItemModel).where(CartItemModel.cart_id == current_user_cart.id).options(joinedload(CartItemModel.product))
    result_items = await session.execute(query_items)
    remaining_items = result_items.scalars().all()

    total = 0
    for i in remaining_items:
        total += i.product.price * i.quantity
    current_user_cart.total_price = total

    await session.commit()

    return {'success': True, 'message': 'Product was deleted from your cart'}


@router.delete('/cart/delete_all_items', tags=['Cart'])
async def delete_all_items(session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    query_user_cart = select(CartModel).where(CartModel.user_id == user_id)
    result_user_cart = await session.execute(query_user_cart)
    current_user_cart = result_user_cart.scalar_one_or_none()

    query_cart_items = select(CartItemModel).where(CartItemModel.cart_id == current_user_cart.id)
    result_cart_items = await session.execute(query_cart_items)
    cart_items = result_cart_items.scalars().all()

    if not cart_items:
        raise HTTPException(status_code=404, detail='Cart not found')

    for item in cart_items:
        await session.delete(item)

    current_user_cart.total_price = 0

    await session.commit()

    return {'success': True, 'message': 'All products was deleted'}