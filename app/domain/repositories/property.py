from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.property import Property
from app.domain.enums import DealType, PropertyType


@dataclass(frozen=True)
class PropertyFilter:
    q: str | None = None
    city: str | None = None
    property_type: PropertyType | None = None
    deal_type: DealType | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_area: float | None = None
    max_area: float | None = None
    rooms: int | None = None
    min_rooms: int | None = None
    max_rooms: int | None = None
    is_active: bool | None = True
    owner_id: int | None = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"


@dataclass(frozen=True)
class PaginatedProperties:
    items: list[Property]
    total: int
    page: int
    page_size: int


class PropertyRepository(ABC):
    @abstractmethod
    def get_by_id(self, property_id: int) -> Property | None:
        raise NotImplementedError

    @abstractmethod
    def add(self, property_obj: Property) -> Property:
        raise NotImplementedError

    @abstractmethod
    def update(self, property_obj: Property) -> Property:
        raise NotImplementedError

    @abstractmethod
    def delete(self, property_obj: Property) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self, filters: PropertyFilter) -> PaginatedProperties:
        raise NotImplementedError
