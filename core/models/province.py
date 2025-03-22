"""
This module defines EUProvince, which represents the smallest building block of the world in
Europa Universalis IV.
"""



from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from . import EUCountry


class ProvinceType(Enum):
    """Enum of province types.
    
    - Owned
    - Native
    - Sea
    - Wasteland
    """
    OWNED = "owned"
    NATIVE = "native"
    SEA = "sea"
    WASTELAND = "wasteland"


class ProvinceTypeColor(Enum):
    """Enum of display colors for each province type.
    
    **Owned** provinces have their own definition from their owner tag.
    - Native -> Sandy brown (203, 164, 103)
    - Sea -> Blue (203, 164, 103)
    - Wasteland -> Grey (128, 128, 128)
    """
    OWNED: tuple[int] = ()
    NATIVE = (203, 164, 103)
    SEA = (55, 90, 220)
    WASTELAND = (128, 128, 128)


@dataclass
class EUProvince:
    """Represents a province on the map.
    
    Has an **update** method that can be used to update the province when loading save data,
    since the default data is always loaded first.

    Attributes:
        province_id (int): The unique ID of the province.
        name (str): The province's name.
        province_type (ProvinceType): The type of province.
        owner (Optional[EUCountry]): The province's owner.
        capital (Optional[str]): The province's capital city.
        culture (Optional[str]): The province's culture.
        religion (Optional[str]): The province's religion.
        base_tax (Optional[int]): The province's tax development.
        base_production (Optional[int]): The province's production development.
        base_manpower (Optional[int]): The province's manpower development.
        native_size (Optional[int]): The number of natives in the province.
        patrol (Optional[int]): The number of game ticks it takes to patrol the province.
        pixel_locations (set[tuple[int, int]]): The set of (x, y) coordinates occupied by the province.
    """
    province_id: int
    name: str
    province_type: ProvinceType
    owner: Optional[EUCountry] = None
    capital: Optional[str] = None
    culture: Optional[str] = None
    religion: Optional[str] = None
    base_tax: Optional[int] = None
    base_production: Optional[int] = None
    base_manpower: Optional[int] = None
    native_size: Optional[int] = None
    patrol: Optional[int] = None
    pixel_locations: set[tuple[int, int]] = field(default_factory=set)

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        """Builds the province from a dictionary."""
        return cls(**data)

    @property
    def bounding_box(self):
        """Gets the bounding box for the province.
        
        The bounding box is defined as the inclusive limits of its x and y values, by
        checking its contained pixels.
        
        Returns:
            tuple[int]: The bounding box.
        """
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
        """Returns the total development of the province.
        
        As wasteland and sea provinces have no development, returns 0 in those cases.
        """
        if not (self.province_type == ProvinceType.SEA or self.province_type == ProvinceType.WASTELAND):
            return self.base_manpower + self.base_production + self.base_tax

        return 0

    def __str__(self):
        return f"Province: {self.name} with ID {self.province_id}"

    def update(self, data: dict[str, str]):
        """Updates the province's attributes.
        
        Checks each key-value pair in the dictionary and updates the associated attribute with that key's name.
        
        Args:
            data (dict[str, str]): The province information to use for updating.
        """
        for key, value in data.items():
            if hasattr(self, key):
                attr_type = type(getattr(self, key))
                try:
                    if attr_type in [str, Optional[str]]:
                        setattr(self, key, value)
                    elif attr_type in [int, Optional[int]]:
                        setattr(self, key, int(value))
                    elif attr_type in [float, Optional[float]]:
                        setattr(self, key, int(float(value)))
                    elif attr_type is ProvinceType:
                        setattr(self, key, ProvinceType(value))
                except:
                    print(f"Error getting data for attribute {key} val {value} for province {self.name}'s attribute type {attr_type}")
