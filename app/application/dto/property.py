from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import DealType, PropertyType


@dataclass(frozen=True)
class CreatePropertyInput:
    title: str
    description: str | None
    city: str
    address: str | None
    property_type: PropertyType
    deal_type: DealType
    price: float
    area: float
    rooms: int | None
    floor: int | None
    total_floors: int | None
    is_active: bool
    owner_id: int


@dataclass(frozen=True)
class PropertyOutput:
    id: int
    title: str
    description: str | None
    city: str
    address: str | None
    property_type: PropertyType
    deal_type: DealType
    price: float
    area: float
    rooms: int | None
    floor: int | None
    total_floors: int | None
    is_active: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class PropertyListOutput:
    total: int
    page: int
    page_size: int
    items: list[PropertyOutput]
