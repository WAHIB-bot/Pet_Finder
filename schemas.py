from pydantic import BaseModel, EmailStr

class SignUpRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    firstName: str
    lastName: str
    phoneNumber: str | None = None

class SignUpResponse(BaseModel):
    user_id: int
