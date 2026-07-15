from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import DealType, PropertyType


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime


class PropertyBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    city: str = Field(min_length=1, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    property_type: PropertyType
    deal_type: DealType
    price: float = Field(gt=0)
    area: float = Field(gt=0)
    rooms: int | None = Field(default=None, ge=0)
    floor: int | None = None
    total_floors: int | None = None
    is_active: bool = True


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    city: str | None = Field(default=None, min_length=1, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    property_type: PropertyType | None = None
    deal_type: DealType | None = None
    price: float | None = Field(default=None, gt=0)
    area: float | None = Field(default=None, gt=0)
    rooms: int | None = Field(default=None, ge=0)
    floor: int | None = None
    total_floors: int | None = None
    is_active: bool | None = None


class PropertyRead(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class PropertyListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[PropertyRead]


class Message(BaseModel):
    message: str
