from enum import Enum


class PropertyType(str, Enum):
    apartment = "apartment"
    house = "house"
    studio = "studio"
    commercial = "commercial"
    land = "land"


class DealType(str, Enum):
    sale = "sale"
    rent = "rent"
