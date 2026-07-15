from fastapi import APIRouter, Depends, Query, status

from app.application.dto.auth import UserOutput
from app.application.dto.property import CreatePropertyInput
from app.application.use_cases.properties import (
    CreatePropertyUseCase,
    DeletePropertyUseCase,
    GetPropertyUseCase,
    ListPropertiesUseCase,
    UpdatePropertyUseCase,
)
from app.domain.enums import DealType, PropertyType
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.repositories.property import PropertyFilter
from app.presentation.dependencies import get_current_user, get_optional_user, get_uow
from app.presentation.schemas import (
    PropertyCreate,
    PropertyListResponse,
    PropertyRead,
    PropertyUpdate,
)

router = APIRouter(prefix="/properties", tags=["properties"])


def _to_read(item) -> PropertyRead:
    return PropertyRead.model_validate(item, from_attributes=True)


@router.post("", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyCreate,
    uow: UnitOfWork = Depends(get_uow),
    current_user: UserOutput = Depends(get_current_user),
) -> PropertyRead:
    result = CreatePropertyUseCase(uow).execute(
        CreatePropertyInput(
            **payload.model_dump(),
            owner_id=current_user.id,
        )
    )
    return _to_read(result)


@router.get("", response_model=PropertyListResponse)
def list_properties(
    q: str | None = Query(default=None, description="Search in title, description, address"),
    city: str | None = None,
    property_type: PropertyType | None = None,
    deal_type: DealType | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_area: float | None = Query(default=None, ge=0),
    max_area: float | None = Query(default=None, ge=0),
    rooms: int | None = Query(default=None, ge=0),
    min_rooms: int | None = Query(default=None, ge=0),
    max_rooms: int | None = Query(default=None, ge=0),
    is_active: bool | None = True,
    owner_id: int | None = None,
    my_only: bool = False,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at", pattern="^(price|area|rooms|created_at)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    uow: UnitOfWork = Depends(get_uow),
    current_user: UserOutput | None = Depends(get_optional_user),
) -> PropertyListResponse:
    filters = PropertyFilter(
        q=q,
        city=city,
        property_type=property_type,
        deal_type=deal_type,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        rooms=rooms,
        min_rooms=min_rooms,
        max_rooms=max_rooms,
        is_active=is_active,
        owner_id=owner_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    result = ListPropertiesUseCase(uow).execute(
        filters,
        my_only=my_only,
        current_user_id=current_user.id if current_user else None,
    )
    return PropertyListResponse(
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        items=[_to_read(item) for item in result.items],
    )


@router.get("/{property_id}", response_model=PropertyRead)
def get_property(property_id: int, uow: UnitOfWork = Depends(get_uow)) -> PropertyRead:
    return _to_read(GetPropertyUseCase(uow).execute(property_id))


@router.patch("/{property_id}", response_model=PropertyRead)
def update_property(
    property_id: int,
    payload: PropertyUpdate,
    uow: UnitOfWork = Depends(get_uow),
    current_user: UserOutput = Depends(get_current_user),
) -> PropertyRead:
    result = UpdatePropertyUseCase(uow).execute(
        property_id,
        current_user.id,
        payload.model_dump(exclude_unset=True),
    )
    return _to_read(result)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: UserOutput = Depends(get_current_user),
) -> None:
    DeletePropertyUseCase(uow).execute(property_id, current_user.id)
