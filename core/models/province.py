from dataclasses import dataclass, field
from enum import Enum
from typing import Optional



class ProvinceType(Enum):
    OWNED = "owned"
    NATIVE = "native"
    SEA = "sea"
    WASTELAND = "wasteland"


class ProvinceTypeColor(Enum):
    OWNED: tuple[int] = ()
    NATIVE = (203, 164, 103)
    SEA = (55, 90, 220)
    WASTELAND = (128, 128, 128)


@dataclass
class EUProvince:
    province_id: int
    name: str
    province_type: ProvinceType
    owner: Optional["EUCountry"] = None
    capital: Optional[str] = None
    culture: Optional[str] = None
    religion: Optional[str] = None
    base_tax: Optional[float] = None
    base_production: Optional[float] = None
    base_manpower: Optional[float] = None
    native_size: Optional[int] = None
    patrol: Optional[int] = None
    pixel_locations: set[tuple[int, int]] = field(default_factory=set)

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        return cls(**data)

    @property
    def bounding_box(self):
        locations = self.pixel_locations
        if not locations:
            return None

        x_values = [x for x, y in locations]
        y_values = [y for x, y in locations]

        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        return (min_x, max_x, min_y, max_y)

    @property
    def development(self):
        if not (self.province_type == ProvinceType.SEA or self.province_type == ProvinceType.WASTELAND):
            return float(self.base_manpower) + float(self.base_production) + float(self.base_tax)

        return 0.000

    def __str__(self):
        return f"Province: {self.name} with ID {self.province_id}"

    def update(self, data: dict[str, str]):
        for key, value in data.items():
            if hasattr(self, key):
                attr_type = type(getattr(self, key))
                try:
                    if attr_type in [str, Optional[str]]:
                        setattr(self, key, value)
                    elif attr_type in [int, Optional[int]]:
                        setattr(self, key, int(value))
                    elif attr_type in [float, Optional[float]]:
                        setattr(self, key, float(value))
                    elif attr_type is ProvinceType:
                        setattr(self, key, ProvinceType(value))
                except:
                    print(f"Error getting data for attribute {key} val {value} for province {self.name}'s attribute type {attr_type}")
