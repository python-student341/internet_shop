from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from envparse import Env
from dotenv import load_dotenv
from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase

from database.hash import config


env = Env()

load_dotenv()


DATABASE_URL = env.str('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, future=True, echo=False)


new_session = async_sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)

SECRET_KEY = env.str("SECRET_KEY")
config.JWT_SECRET_KEY = SECRET_KEY

async def get_session():
    async with new_session() as session:
        yield session

session_dep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass