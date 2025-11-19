from fastapi import APIRouter, HTTPException, Cookie, Response
from sqlalchemy import select, delete

from models.models import UserModel
from schemas.user_schemas import CreateUserSchema, LoginUserSchema, CPSchema, CNSchema, DeleteUserSchema
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

    new_user = UserModel(
        email=data.email,
        name=data.name,
        password=hashing_password(data.password)   
    )

    session.add(new_user)
    await session.commit()

    return {'success': True, 'message': 'User was added', 'info': new_user}


@router.post('/users/sign_in', tags=['Users'])
async def sign_in(data: LoginUserSchema, session: session_dep, response: Response):

    query = select(UserModel).where(UserModel.email == data.email)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not current_user:
        return {'success': False, 'message': 'User not found'}

    if not pwd_context.verify(data.password, current_user.password):
        return {'success': False, 'message': 'Incorrect password'}

    token = security.create_access_token(uid=str(current_user.id))
    response.set_cookie(key=config.JWT_ACCESS_COOKIE_NAME, value=token, httponly=True, samesite='Lax', max_age=60*60)

    return {'success': True, 'message': 'Login successful', 'token': token}


@router.put('/users/change_password', tags=['Users'])
async def change_password(id: int, data: CPSchema, session: session_dep, token: str = Cookie(None)):
    
    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    if user_id != id:
        return {'success': False, 'message': 'You can only change your own data'}

    query = select(UserModel).where(UserModel.id == id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not pwd_context.verify(data.old_password, current_user.password):
        return {'success': False, 'message': "Incorrect password"}

    if data.new_password != data.repeat_new_password:
        return {'success': False, 'message': "The passwords don't match"}

    current_user.password = hashing_password(data.new_password)

    await session.commit()
    await session.refresh(current_user)

    return {'success': True, 'message': 'Password was changed'}


@router.put('/users/change_name', tags=['Users'])
async def change_name(id: int, data: CNSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if user_id != id:
        return {'success': False, 'message': 'You can only change your own data'}

    if not pwd_context.verify(data.password, current_user.password):
        return {'success': False, 'message': 'Incorrect password'}

    current_user.name = data.new_name

    await session.commit()
    await session.refresh(current_user)

    return {'success': True, 'message': 'Name was changed'}


@router.delete('/users/delete_user', tags=['Users'])
async def delete_user(id: int, data: DeleteUserSchema, session: session_dep, token: str = Cookie(None)):

    if not token:
        return {'success': False, 'message': 'No token'}

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if user_id != id:
        return {'success': False, 'message': 'You can only change your own data'}

    if not pwd_context.verify(data.password, current_user.password):
        return {'success': False, 'message': 'Incorrect password'}

    deleted_user = delete(UserModel).where(UserModel.id == id)

    await session.execute(deleted_user)
    await session.commit()

    return {'success': True, 'message': 'User was deleted'}