from pydantic import BaseModel, ConfigDict

from app.schema.user import UserSchema


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    user: UserSchema
    model_config = ConfigDict(from_attributes=True)
