from pydantic import Field, BaseModel


class CreateCardShema(BaseModel):
    user_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    card_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    repeat_card_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')

class UpdateBalanceSchema(BaseModel):
    amount: int = Field(ge=1, le=1000000)
    card_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')

class ChangeCardPasswordSchema(BaseModel):
    old_card_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    new_card_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
    repeat_new_card_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')

class DeleteCardSchema(BaseModel):
    card_password: str = Field(min_length=8, max_length=25, pattern=r'^[a-zA-Z0-9@#$%^&+=]+$')
