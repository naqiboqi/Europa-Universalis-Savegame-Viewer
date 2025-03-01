from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProvinceType(Enum):
    OWNED = "owned"
    NATIVE = "native"
    SEA = "sea"
    WASTELAND = "wasteland"


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

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        return cls(**data)

    def __str__(self):
        return f"Province: {self.name} with ID {self.province_id}"