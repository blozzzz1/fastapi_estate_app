from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.domain.entities.property import Property
from app.domain.repositories.property import PaginatedProperties, PropertyFilter, PropertyRepository
from app.infrastructure.orm.mappers import apply_property_to_model, property_to_entity
from app.infrastructure.orm.models import PropertyModel


class SqlAlchemyPropertyRepository(PropertyRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, property_id: int) -> Property | None:
        model = self._session.get(PropertyModel, property_id)
        return property_to_entity(model) if model else None

    def add(self, property_obj: Property) -> Property:
        model = PropertyModel(
            title=property_obj.title,
            description=property_obj.description,
            city=property_obj.city,
            address=property_obj.address,
            property_type=property_obj.property_type,
            deal_type=property_obj.deal_type,
            price=property_obj.price,
            area=property_obj.area,
            rooms=property_obj.rooms,
            floor=property_obj.floor,
            total_floors=property_obj.total_floors,
            is_active=property_obj.is_active,
            owner_id=property_obj.owner_id,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return property_to_entity(model)

    def update(self, property_obj: Property) -> Property:
        assert property_obj.id is not None
        model = self._session.get(PropertyModel, property_obj.id)
        if model is None:
            raise ValueError("Property model not found for update")
        apply_property_to_model(model, property_obj)
        self._session.flush()
        self._session.refresh(model)
        return property_to_entity(model)

    def delete(self, property_obj: Property) -> None:
        assert property_obj.id is not None
        model = self._session.get(PropertyModel, property_obj.id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def list(self, filters: PropertyFilter) -> PaginatedProperties:
        query = self._session.query(PropertyModel)

        if filters.is_active is not None:
            query = query.filter(PropertyModel.is_active.is_(filters.is_active))
        if filters.city:
            query = query.filter(PropertyModel.city.ilike(f"%{filters.city}%"))
        if filters.property_type:
            query = query.filter(PropertyModel.property_type == filters.property_type)
        if filters.deal_type:
            query = query.filter(PropertyModel.deal_type == filters.deal_type)
        if filters.min_price is not None:
            query = query.filter(PropertyModel.price >= filters.min_price)
        if filters.max_price is not None:
            query = query.filter(PropertyModel.price <= filters.max_price)
        if filters.min_area is not None:
            query = query.filter(PropertyModel.area >= filters.min_area)
        if filters.max_area is not None:
            query = query.filter(PropertyModel.area <= filters.max_area)
        if filters.rooms is not None:
            query = query.filter(PropertyModel.rooms == filters.rooms)
        if filters.min_rooms is not None:
            query = query.filter(PropertyModel.rooms >= filters.min_rooms)
        if filters.max_rooms is not None:
            query = query.filter(PropertyModel.rooms <= filters.max_rooms)
        if filters.owner_id is not None:
            query = query.filter(PropertyModel.owner_id == filters.owner_id)
        if filters.q:
            like = f"%{filters.q}%"
            query = query.filter(
                or_(
                    PropertyModel.title.ilike(like),
                    PropertyModel.description.ilike(like),
                    PropertyModel.address.ilike(like),
                )
            )

        sort_column = getattr(PropertyModel, filters.sort_by)
        query = query.order_by(sort_column.asc() if filters.sort_order == "asc" else sort_column.desc())

        total = query.count()
        models = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size).all()
        return PaginatedProperties(
            items=[property_to_entity(model) for model in models],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )
