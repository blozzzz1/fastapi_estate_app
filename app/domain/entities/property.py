from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import DealType, PropertyType


@dataclass
class Property:
    id: int | None
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
    created_at: datetime | None = None
    updated_at: datetime | None = None
