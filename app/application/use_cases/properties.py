from dataclasses import replace

from app.application.dto.property import CreatePropertyInput, PropertyListOutput, PropertyOutput
from app.domain.entities.property import Property
from app.domain.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.repositories.property import PropertyFilter


def _to_output(property_obj: Property) -> PropertyOutput:
    assert property_obj.id is not None
    assert property_obj.created_at is not None
    assert property_obj.updated_at is not None
    return PropertyOutput(
        id=property_obj.id,
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
        created_at=property_obj.created_at,
        updated_at=property_obj.updated_at,
    )


class CreatePropertyUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, data: CreatePropertyInput) -> PropertyOutput:
        property_obj = Property(
            id=None,
            title=data.title,
            description=data.description,
            city=data.city,
            address=data.address,
            property_type=data.property_type,
            deal_type=data.deal_type,
            price=data.price,
            area=data.area,
            rooms=data.rooms,
            floor=data.floor,
            total_floors=data.total_floors,
            is_active=data.is_active,
            owner_id=data.owner_id,
        )
        created = self._uow.properties.add(property_obj)
        self._uow.commit()
        return _to_output(created)


class GetPropertyUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, property_id: int) -> PropertyOutput:
        property_obj = self._uow.properties.get_by_id(property_id)
        if property_obj is None:
            raise NotFoundError("Property not found")
        return _to_output(property_obj)


class ListPropertiesUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, filters: PropertyFilter, *, my_only: bool, current_user_id: int | None) -> PropertyListOutput:
        if my_only and current_user_id is None:
            raise AuthenticationError("Not authenticated")

        effective = filters
        if my_only and current_user_id is not None:
            effective = replace(filters, owner_id=current_user_id)

        result = self._uow.properties.list(effective)
        return PropertyListOutput(
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            items=[_to_output(item) for item in result.items],
        )


class UpdatePropertyUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, property_id: int, owner_id: int, fields: dict) -> PropertyOutput:
        property_obj = self._uow.properties.get_by_id(property_id)
        if property_obj is None:
            raise NotFoundError("Property not found")
        if property_obj.owner_id != owner_id:
            raise AuthorizationError("Not enough permissions")

        updated_entity = replace(property_obj, **fields)
        saved = self._uow.properties.update(updated_entity)
        self._uow.commit()
        return _to_output(saved)


class DeletePropertyUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, property_id: int, owner_id: int) -> None:
        property_obj = self._uow.properties.get_by_id(property_id)
        if property_obj is None:
            raise NotFoundError("Property not found")
        if property_obj.owner_id != owner_id:
            raise AuthorizationError("Not enough permissions")

        self._uow.properties.delete(property_obj)
        self._uow.commit()
