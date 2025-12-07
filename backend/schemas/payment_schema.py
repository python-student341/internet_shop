from pydantic import BaseModel

class PayItemSchema(BaseModel):
    cart_item_id: int