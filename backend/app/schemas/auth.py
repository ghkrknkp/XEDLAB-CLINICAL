from pydantic import BaseModel, Field

try:
    from pydantic import EmailStr
    _email_type = EmailStr
except Exception:
    _email_type = str  # Fallback: treat email as plain string


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
