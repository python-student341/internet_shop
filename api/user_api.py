from fastapi import APIRouter, HTTPException, Cookie, Response
from sqlalchemy import select, delete

from models.models import UserModel, CartModel
from schemas.user_schemas import CreateUserSchema, LoginUserSchema, ChangePasswordSchema, ChangeNameSchema, DeleteUserSchema
from database.database import session_dep
from database.hash import hashing_password, pwd_context, security, config


router = APIRouter()


@router.post('/users/sign_up', tags=['Users'])
async def sign_up(data: CreateUserSchema, session: session_dep):

    if data.password != data.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    exiting_user = await session.execute(select(UserModel).where(UserModel.email == data.email))

    if exiting_user.scalar_one_or_none():
        raise HTTPException(status_code=409, detail='This email already exits in database')

    if data.password != data.repeat_password:
        raise HTTPException(status_code=400, detail="The passwords don't match")

    new_user = UserModel(
        email=data.email,
        name=data.name,
        password=hashing_password(data.password)   
    )

    session.add(new_user)
    await session.flush()

    new_cart = CartModel(
        user_id=new_user.id
    )

    session.add(new_cart)
    await session.commit()

    return {'success': True, 'message': 'User was added', 'info': new_user}


@router.post('/users/sign_in', tags=['Users'])
async def sign_in(data: LoginUserSchema, session: session_dep, response: Response):

    query = select(UserModel).where(UserModel.email == data.email)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    if not pwd_context.verify(data.password, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    token = security.create_access_token(uid=str(current_user.id))
    response.set_cookie(key=config.JWT_ACCESS_COOKIE_NAME, value=token, httponly=True, samesite='Lax', max_age=60*60)

    return {'success': True, 'message': 'Login successful', 'token': token}


@router.get('/users/get_info', tags=['Users'])
async def get_info(session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail='No token')

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    return {'success': True, 'info': {'id': current_user.id, 'email': current_user.email, 'name': current_user.name}}


@router.put('/users/change_password', tags=['Users'])
async def change_password(data: ChangePasswordSchema, session: session_dep, token: str = Cookie):
    
    if not token:
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not pwd_context.verify(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    if data.new_password != data.repeat_new_password:
        raise HTTPException(status_code=400, detail="The passwords don't match")

    current_user.password = hashing_password(data.new_password)

    await session.commit()
    await session.refresh(current_user)

    return {'success': True, 'message': 'Password was changed'}


@router.put('/users/change_name', tags=['Users'])
async def change_name(data: ChangeNameSchema, session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not pwd_context.verify(data.password, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    current_user.name = data.new_name

    await session.commit()
    await session.refresh(current_user)

    return {'success': True, 'message': 'Name was changed'}


@router.delete('/users/delete_user', tags=['Users'])
async def delete_user(data: DeleteUserSchema, session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not pwd_context.verify(data.password, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    await session.delete(current_user)
    await session.commit()

    return {'success': True, 'message': 'User was deleted'}