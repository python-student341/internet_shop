from fastapi import APIRouter, HTTPException, Cookie, Depends, UploadFile, File, Form
from sqlalchemy import select, delete
import os

from models.models import CategoryModel, ProductModel, UserModel
from schemas.category_schema import CategoryShema, ChangeCategoryNameSchema
from schemas.product_schema import ProductSchema, ChangeProductNameSchema, ChangeProductPriceSchema
from database.database import session_dep
from database.hash import security, decode_token


router = APIRouter()


#-----------Category----------#
@router.post('/category/add_category', tags=['For admin'])
async def add_category(data: CategoryShema, session: session_dep, token: str = Cookie(...)):

    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = decode_token(token)
    user_id = int(payload["sub"])

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not an admin")

    current_category = await session.execute(select(CategoryModel).where(CategoryModel.name == data.name))
    
    if current_category.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='Category with this name already exists')

    new_category = CategoryModel(
        name=data.name
    )

    session.add(new_category)
    await session.commit()

    return {'success': True, 'message': 'Category was added', 'Category': new_category}


@router.put('/category/change_category_name', tags=['For admin'])
async def change_category_name(category_id: int, data: ChangeCategoryNameSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    try:
        payload = security._decode_token(token)

        if payload.type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not payload.fresh:
            raise HTTPException(status_code=401, detail="Token not fresh")
        
        user_id = int(payload.sub)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    category_query = select(CategoryModel).where(CategoryModel.id == category_id)
    category_result = await session.execute(category_query)
    current_category = category_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not an admin")

    if not current_category:
        raise HTTPException(status_code=404, detail='Category not found')

    exiting_category = await session.execute(select(CategoryModel).where(CategoryModel.name == data.new_name))

    if exiting_category.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Category with this name already exists")

    current_category.name = data.new_name

    await session.commit()
    await session.refresh(current_category)

    return {'success': True, 'message': 'Category name was changed'}


@router.delete('/category/delete_category', tags=['For admin'])
async def delete_category(category_id: int, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    try:
        payload = security._decode_token(token)

        if payload.type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not payload.fresh:
            raise HTTPException(status_code=401, detail="Token not fresh")
        
        user_id = int(payload.sub)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    category_query = select(CategoryModel).where(CategoryModel.id == category_id)
    category_result = await session.execute(category_query)
    current_category = category_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not an admin")

    if not current_category:
        raise HTTPException(status_code=404, detail='Category not found')

    deleted_category = delete(CategoryModel).where(CategoryModel.id == category_id)

    await session.execute(deleted_category)
    await session.commit()

    return {'success': True, 'message': 'Category was deleted'}



#-----------Products----------#
@router.post('/category/product/add_product', tags=['For admin'])
async def add_product(session: session_dep, category_id: int, name: str = Form(...), price: float = Form(...), image: UploadFile = File(...), token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    try:
        payload = security._decode_token(token)

        if payload.type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not payload.fresh:
            raise HTTPException(status_code=401, detail="Token not fresh")
        
        user_id = int(payload.sub)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    category_query = select(CategoryModel).where(CategoryModel.id == category_id)
    category_result = await session.execute(category_query)
    current_category = category_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not an admin")

    if not current_category:
        raise HTTPException(status_code=404, detail='Category not found')

    file_path = f"static/images/{image.filename}"

    with open(file_path, "wb") as f:
        f.write(await image.read())

    data = ProductSchema(name=name, price=price)

    new_product = ProductModel(
        name=data.name,
        image_path=file_path,
        price=data.price,
        category_id=current_category.id
    )

    session.add(new_product)
    await session.commit()

    return {'success': True, 'message': 'Product was added', 'Product': new_product}


@router.put('/category/product/change_product_name', tags=['For admin'])
async def change_product_name(product_id: int, data: ChangeProductNameSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    try:
        payload = security._decode_token(token)

        if payload.type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not payload.fresh:
            raise HTTPException(status_code=401, detail="Token not fresh")
        
        user_id = int(payload.sub)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    product_query = select(ProductModel).where(ProductModel.id == product_id)
    product_result = await session.execute(product_query)
    current_product = product_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not an admin")

    if not current_product:
        raise HTTPException(status_code=404, detail='Product not found')

    exiting_product = await session.execute(select(ProductModel).where(ProductModel.name == data.new_name))

    if exiting_product.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Product with this name already exists")

    current_product.name = data.new_name

    await session.commit()
    await session.refresh(current_product)

    return {'success': True, 'message': 'Product name was changed'}


@router.put('/category/product/change_product_price', tags=['For admin'])
async def change_product_price(product_id: int, data: ChangeProductPriceSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    try:
        payload = security._decode_token(token)

        if payload.type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not payload.fresh:
            raise HTTPException(status_code=401, detail="Token not fresh")
        
        user_id = int(payload.sub)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    product_query = select(ProductModel).where(ProductModel.id == product_id)
    product_result = await session.execute(product_query)
    current_product = product_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not an admin")

    if not current_product:
        raise HTTPException(status_code=404, detail='Product not found')

    current_product.price = data.new_price

    await session.commit()
    await session.refresh(current_product)

    return {'success': True, 'message': 'Product price was updated'}


@router.put('/category/product/change_product_image', tags=['For admin'])
async def change_product_image(product_id: int, session: session_dep, image: UploadFile = File(...), token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    try:
        payload = security._decode_token(token)

        if payload.type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not payload.fresh:
            raise HTTPException(status_code=401, detail="Token not fresh")
        
        user_id = int(payload.sub)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    product_query = select(ProductModel).where(ProductModel.id == product_id)
    product_result = await session.execute(product_query)
    current_product = product_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail='You are not an admin')

    if not current_product:
        raise HTTPException(status_code=404, detail='Product not found')

    file_path = f"static/images/{image.filename}"
    with open(file_path, "wb") as f:
        f.write(await image.read())

    if os.path.exists(current_product.image):
        os.remove(current_product.image)

    current_product.image = file_path

    await session.commit()
    await session.refresh(current_product)

    return {'success': True, 'message': 'Image was changed', 'image': file_path}


@router.delete('/category/product/delete_product', tags=['For admin'])
async def delete_product(product_id: int, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    try:
        payload = security._decode_token(token)

        if payload.type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not payload.fresh:
            raise HTTPException(status_code=401, detail="Token not fresh")
        
        user_id = int(payload.sub)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    product_query = select(ProductModel).where(ProductModel.id == product_id)
    product_result = await session.execute(product_query)
    current_product = product_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail='You are not an admin')

    if not current_product:
        raise HTTPException(status_code=404, detail='Product not found')

    deleted_product = select(ProductModel).where(ProductModel.id == product_id)

    await session.execute(deleted_product)
    await session.commit()

    return {'success': True, 'message': 'Product was deleted from list'}