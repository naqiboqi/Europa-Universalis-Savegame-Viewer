"""
This module defines EUProvince, which represents the smallest building block of the world in
Europa Universalis IV.
"""



from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import floor
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

    Attributes:
        province_id (int): The unique ID of the province.
        name (str): The province's name.
        province_type (ProvinceType): The type of province.
        owner (Optional[EUCountry]): The province's owner.
        capital (Optional[str]): The province's capital city.
        is_capital (Optional[bool]): If the province is the capital of its country.
        is_hre (Optional[bool]): If the province is within the Holy Roman Empire.
        culture (Optional[str]): The province's culture.
        religion (Optional[str]): The province's religion.
        base_tax (Optional[int]): The province's tax development.
        base_production (Optional[int]): The province's production development.
        base_manpower (Optional[int]): The province's manpower development.
        trade_goods (Optional[str]): The dominant trade good produced by the province.
        trade_power (Optional[float]): The province's trade power.
            Higher levels indicate stronger influence on that province's trade node.
        center_of_trade (Optional[int]): The province's center of trade level.
            Higher levels indicate stronger trade power and development.
        local_autonomy (Optional[float]): The province's autonomy and degree of separation.
            Higher levels indicate less production and power contribution to the owning country.
        devastation (Optional[int]): The amount of devastation in the province.
            Higher levels indicate less production and power contribution to the owning country.
        unrest (Optional[int]): The amount of unrest in the province.
            Higher levels indicate a higher likelyhood of rebellion.
        trade_node (Optional[str]): The trade node that the province belongs to.
        garrison (Optional[int]): The province's fort garrison population.
        fort_level (Optional[int]): The province's fort level. 
            Higher levels indicate a stronger fort and make the province harder to siege and occupy.
        native_size (Optional[int]): The number of natives in the province.
        patrol (Optional[int]): The number of game ticks it takes to patrol the province (only if it a sea province).
        pixel_locations (set[tuple[int, int]]): The set of (x, y) coordinates occupied by the province.
    """
    province_id: int
    name: str
    province_type: ProvinceType
    owner: Optional[EUCountry] = None
    capital: Optional[str] = None
    is_capital: Optional[bool] = False
    is_hre: Optional[bool] = False
    culture: Optional[str] = None
    religion: Optional[str] = None
    base_tax: Optional[int] = None
    base_production: Optional[int] = None
    base_manpower: Optional[int] = None
    trade_goods: Optional[str] = None
    trade_power: Optional[float] = None
    center_of_trade: Optional[int] = None
    local_autonomy: Optional[float] = None
    devastation: Optional[int] = None
    unrest: Optional[int] = None
    trade_node: Optional[str] = None
    garrison: Optional[int] = None
    fort_level: Optional[int] = None
    native_size: Optional[int] = None
    patrol: Optional[int] = None
    pixel_locations: set[tuple[int, int]] = field(default_factory=set)

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        """Builds the province from a dictionary."""
        converted_data = {}

        for key, value in data.items():
            if key in cls.__annotations__:

                attr_type = cls.__annotations__[key]
                try:
                    if attr_type in ["str", "Optional[str]"]:
                        converted_data[key] = value
                    elif attr_type in ["int", "Optional[int]"]:
                        converted_data[key] = int(float(value))
                    elif attr_type in ["float", "Optional[float]"]:
                        converted_data[key] = float(value)
                    elif attr_type == "ProvinceType":
                        converted_data[key] = ProvinceType(value)
                    else:
                        converted_data[key] = value
                except (ValueError, TypeError) as e:
                    print(f"Error converting {key} with value {value}: {e}")

        return cls(**converted_data)

    @property
    def area_km2(self):
        """Returns the estimated area of the province in square kilometers 
        using the total world map size and its pixel resolution.
        """
        world_area_km2 = 510_100_100
        map_width, map_height = 5632, 2304
        scale_factor = world_area_km2 / (map_width * map_height)

        return round(len(self.pixel_locations) * scale_factor, 2)

    @property
    def bounding_box(self):
        """Gets the bounding box for the province.
        
        The bounding box is defined as the inclusive limits of its `(x, y)` pixel locations.
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

    @property
    def autonomy_modifier(self):
        if self.local_autonomy:
            return 1 - (self.local_autonomy / 100)
        return 1.00

    @property
    def tax_income(self):
        """The monthly tax income of the province in ducats."""
        annual_income = self.base_tax * 0.5 * self.autonomy_modifier
        return round(annual_income / 12, 2)

    @property
    def base_production_income(self):
        """The monthly production income of the province before applying the trade good price."""
        annual_income = self.goods_produced * self.autonomy_modifier
        return round(annual_income, 2)

    @property
    def income(self):
        """The total monthly income of the province in ducats."""
        return self.tax_income + self.base_production_income

    @property
    def goods_produced(self):
        """The amount of goods produced by the province. Is based on the province's `base_production`."""
        return round(self.base_production * 0.10 * self.autonomy_modifier, 2)

    @property
    def manpower(self):
        """The amount of manpower contributed by the province. Is based on the province's `base_manpower`."""
        return floor(self.base_manpower * 125 * self.autonomy_modifier) + 250

    @property
    def sailors(self):
        """The amount of sailors contributed by the province. Is based on the province's `base_production`."""
        return floor(self.base_production * 30 * self.autonomy_modifier)

    def __str__(self):
        return f"Province: {self.name} with ID {self.province_id}"
