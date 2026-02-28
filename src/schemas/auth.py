from pydantic import BaseModel


class ReqRegister(BaseModel):
    phone_number: str
    password: str


class AccessToken(BaseModel):
    access_token: str
