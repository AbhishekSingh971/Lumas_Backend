from pydantic import BaseModel, Field

class ProfileUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=80)
    last_name: str | None = Field(default=None, max_length=80)
    display_name: str | None = Field(default=None, max_length=120)
    username: str | None = Field(default=None, min_length=3, max_length=40)
    avatar_url: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=30)
    phone_country_code: str | None = Field(default=None, max_length=10)
    locale: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=80)
    country: str | None = Field(default=None, max_length=80)
    bio: str | None = Field(default=None, max_length=500)

class NotificationPreferencesRequest(BaseModel):
    email: bool | None = None
    push: bool | None = None
    product_updates: bool | None = None
    security_alerts: bool | None = None
