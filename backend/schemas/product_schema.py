from pydantic import BaseModel, Field


class ProductSchema(BaseModel):
    name: str = Field(min_length=3, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')
    price: float = Field(ge=1)

class ChangeProductNameSchema(BaseModel):
    new_name: str = Field(min_length=3, max_length=25, pattern=r'^[a-zA-Zа-яА-Я\s]+$')

class ChangeProductPriceSchema(BaseModel):
    new_price: float = Field(ge=1)