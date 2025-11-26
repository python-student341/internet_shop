from fastapi import APIRouter, HTTPException, Cookie, Response
from sqlalchemy import select, delete
import random

from models.models import CardModel, UserModel
from schemas.card_schema import CreateCardShema, UpdateBalanceSchema, ChangeCardPasswordSchema, DeleteCardSchema
from database.database import session_dep
from database.hash import hashing_password, pwd_context, security, config


router = APIRouter()


@router.post('/card/create_card', tags=['Card'])
async def create_card(data: CreateCardShema, session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail='User not found')

    if not pwd_context.verify(data.user_password, current_user.password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    if data.card_password != data.repeat_card_password:
        return {'success': False, 'message': "The passwords don't match"}

    exiting_card = await session.execute(select(CardModel).where(CardModel.user_id == user_id))

    if exiting_card.scalar_one_or_none():
        return {'success': False, 'message': 'You already have a card'}

    card = CardModel(
        user_id=user_id,
        card=random.randint(1000000000000000, 9999999999999999),
        card_password=hashing_password(data.card_password),
        balance=0
    )

    session.add(card)
    await session.commit()

    return {'success': True, 'message': 'Card was created', 'info': card}


@router.put('/card/add_balance', tags=['Card'])
async def add_balance(data: UpdateBalanceSchema, session: session_dep, token: str = Cookie):
    
    if not token: 
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(CardModel).where(CardModel.user_id == user_id)
    result = await session.execute(query)
    current_card = result.scalar_one_or_none()

    if not current_card:
        raise HTTPException(status_code=404, detail='Card not found')
    
    card_password=data.card_password
    amount=data.amount

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    if not pwd_context.verify(card_password, current_card.card_password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    current_card.balance += amount

    await session.commit()
    await session.refresh(current_card)

    return {'success': True, 'message': 'Balance was updated', 'Your balance': current_card.balance}


@router.get('/card/get_balance', tags=['Card'])
async def get_balance(session: session_dep, token: str = Cookie):
    
    if not token:
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub) 

    query = select(CardModel).where(CardModel.user_id == user_id)
    result = await session.execute(query)
    current_card = result.scalar_one_or_none()

    if not current_card:
        raise HTTPException(status_code=404, detail='Card not found')

    return {'success': True, 'balance': current_card.balance}


@router.get('/card/get_info', tags=['Card'])
async def get_info(session: session_dep, token: str = Cookie):
    
    if not token:
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub) 

    query = select(CardModel).where(CardModel.user_id == user_id)
    result = await session.execute(query)
    current_card = result.scalar_one_or_none()

    if not current_card:
        raise HTTPException(status_code=404, detail='Card not found')

    return {'success': True, 'info': current_card}


@router.put('/card/change_password', tags=['Card'])
async def change_card_password(data: ChangeCardPasswordSchema, session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(CardModel).where(CardModel.user_id == user_id)
    result = await session.execute(query)
    current_card = result.scalar_one_or_none()

    if not current_card:
        raise HTTPException(status_code=404, detail='Card not found')

    if not pwd_context.verify(data.old_card_password, current_card.card_password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    if data.new_card_password != data.repeat_new_card_password:
        raise HTTPException(status_code=400, detail="The passwords don't match")

    current_card.card_password = hashing_password(data.new_card_password)

    await session.commit()
    await session.refresh(current_card)

    return {'success': True, 'message': 'Password was changed'}


@router.delete('/card/delete_card', tags=['Card'])
async def delete_card(data: DeleteCardSchema, session: session_dep, token: str = Cookie):

    if not token:
        raise HTTPException(status_code=401, detail="No token")

    payload = security._decode_token(token)
    user_id = int(payload.sub)

    query = select(CardModel).where(CardModel.user_id == user_id)
    result = await session.execute(query)
    current_card = result.scalar_one_or_none()

    if not current_card:
        raise HTTPException(status_code=404, detail='Card not found')

    if not pwd_context.verify(data.card_password, current_card.card_password):
        raise HTTPException(status_code=400, detail='Incorrect password')

    await session.delete(current_card)
    await session.commit()

    return {'success': True, 'message': 'Card was deleted'}