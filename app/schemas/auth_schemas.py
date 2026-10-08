from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(default="", max_length=80)
    display_name: str | None = Field(default=None, max_length=120)
    locale: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=80)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str):
        classes = [any(c.islower() for c in value), any(c.isupper() for c in value), any(c.isdigit() for c in value)]
        if sum(classes) < 2:
            raise ValueError("Password must contain at least two of: lowercase, uppercase, number")
        return value

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=300)
    password: str = Field(min_length=10, max_length=128)

class GoogleAuthRequest(BaseModel):
    id_token: str = Field(min_length=20)
