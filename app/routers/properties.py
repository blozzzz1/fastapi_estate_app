from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_optional_user
from app.models import DealType, Property, PropertyType, User
from app.schemas import PropertyCreate, PropertyListResponse, PropertyRead, PropertyUpdate

router = APIRouter(prefix="/properties", tags=["properties"])


@router.post("", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Property:
    property_obj = Property(**payload.model_dump(), owner_id=current_user.id)
    db.add(property_obj)
    db.commit()
    db.refresh(property_obj)
    return property_obj


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
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> PropertyListResponse:
    if my_only and current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    query = db.query(Property)

    if is_active is not None:
        query = query.filter(Property.is_active.is_(is_active))
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if deal_type:
        query = query.filter(Property.deal_type == deal_type)
    if min_price is not None:
        query = query.filter(Property.price >= min_price)
    if max_price is not None:
        query = query.filter(Property.price <= max_price)
    if min_area is not None:
        query = query.filter(Property.area >= min_area)
    if max_area is not None:
        query = query.filter(Property.area <= max_area)
    if rooms is not None:
        query = query.filter(Property.rooms == rooms)
    if min_rooms is not None:
        query = query.filter(Property.rooms >= min_rooms)
    if max_rooms is not None:
        query = query.filter(Property.rooms <= max_rooms)
    if owner_id is not None:
        query = query.filter(Property.owner_id == owner_id)
    if my_only and current_user is not None:
        query = query.filter(Property.owner_id == current_user.id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Property.title.ilike(like),
                Property.description.ilike(like),
                Property.address.ilike(like),
            )
        )

    sort_column = getattr(Property, sort_by)
    query = query.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PropertyListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{property_id}", response_model=PropertyRead)
def get_property(property_id: int, db: Session = Depends(get_db)) -> Property:
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if property_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return property_obj


@router.patch("/{property_id}", response_model=PropertyRead)
def update_property(
    property_id: int,
    payload: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Property:
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if property_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    if property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(property_obj, field, value)

    db.commit()
    db.refresh(property_obj)
    return property_obj


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if property_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    if property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    db.delete(property_obj)
    db.commit()
