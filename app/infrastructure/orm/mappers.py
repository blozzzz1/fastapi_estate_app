from app.domain.entities.property import Property
from app.domain.entities.user import User
from app.infrastructure.orm.models import PropertyModel, UserModel


def user_to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        full_name=model.full_name,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def property_to_entity(model: PropertyModel) -> Property:
    return Property(
        id=model.id,
        title=model.title,
        description=model.description,
        city=model.city,
        address=model.address,
        property_type=model.property_type,
        deal_type=model.deal_type,
        price=model.price,
        area=model.area,
        rooms=model.rooms,
        floor=model.floor,
        total_floors=model.total_floors,
        is_active=model.is_active,
        owner_id=model.owner_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_property_to_model(model: PropertyModel, entity: Property) -> None:
    model.title = entity.title
    model.description = entity.description
    model.city = entity.city
    model.address = entity.address
    model.property_type = entity.property_type
    model.deal_type = entity.deal_type
    model.price = entity.price
    model.area = entity.area
    model.rooms = entity.rooms
    model.floor = entity.floor
    model.total_floors = entity.total_floors
    model.is_active = entity.is_active
    model.owner_id = entity.owner_id
