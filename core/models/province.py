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
    owner: Optional[str] = None
    capital: Optional[str] = None
    culture: Optional[str] = None
    religion: Optional[str] = None
    base_tax: Optional[int] = None
    base_production: Optional[int] = None
    base_manpower: Optional[int] = None
    native_size: Optional[int] = None
    patrol: Optional[int] = None
    pixel_locations: list[tuple] = field(default_factory=list)

    @property
    def development(self):
        return self.base_manpower + self.base_production + self.base_tax

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        return cls(**data)

    def __str__(self):
        return f"Province: {self.name} with ID {self.province_id}"