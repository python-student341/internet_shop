from pydantic import BaseModel, Field

class CartItemSchema(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=100)

class DeleteItemSchema(BaseModel):
    cart_item_id: int

class DeleteOneItemSchema(BaseModel):
    cart_item_id: int
    amount: int