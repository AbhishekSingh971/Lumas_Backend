from typing import Any
from pydantic import BaseModel, Field

class DeviceRegisterRequest(BaseModel):
    installation_id: str = Field(min_length=8, max_length=200)
    platform: str = Field(pattern="^(android|ios|web|windows|macos|linux)$")
    device: dict[str, Any] = {}
    notification: dict[str, Any] = {}

class WebPushSubscriptionRequest(BaseModel):
    device_id: str
    endpoint: str = Field(min_length=20, max_length=2000)
    p256dh: str = Field(min_length=10)
    auth: str = Field(min_length=5)
