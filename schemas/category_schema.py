from pydantic import BaseModel, Field
from typing import Optional
from fastapi import UploadFile


class CategoryShema(BaseModel):
    name: str = Field(min_length=3, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')

class ChangeCategoryNameSchema(BaseModel):
    new_name: str = Field(min_length=3, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')