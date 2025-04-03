"""
This module defines EUArea, which represents a collection of provinces in Europa Universalis IV.
"""



from dataclasses import dataclass, field
from typing import Optional

from . import EUMapEntity, EUProvince, ProvinceType
from ..utils import MapUtils



@dataclass
class EUArea(EUMapEntity):
    """Represents an area on the map.

    Inherits attributes from `EUMapEntity`.
    
    Attributes:
        area_id (str): The area's in-game identifier.
        provinces (dict[int, EUProvince]): A mapping of province IDs to EUProvinces
            that belong to the area.

        pixel_locations (set[tuple[int, int]]): The set of (x, y) coordinates occupied by the entity.
    """
    area_id: str
    provinces: dict[int, EUProvince]

    pixel_locations: Optional[set[tuple[int, int]]] = field(init=False)

    def __post_init__(self):
        """Aggregate pixel locations from the contained provinces."""
        self.pixel_locations = set(loc for province in self.provinces.values() for loc in province.pixel_locations)
        super().__post_init__()

    @classmethod
    def from_dict(cls, data: dict[str, str|dict]):
        """Builds the area from a dictionary."""
        return cls(**data)

    @classmethod
    def name_from_id(cls, area_id: str):
        """Gets the area name from the area ID for displaying.
        
        Args:
            area_id (str): The area ID.

        Returns:
            str: The display name.
        """
        name_split = area_id.removesuffix("area").replace("_", " ").split()
        return " ".join(name.capitalize() for name in name_split)

    @property
    def development(self):
        """Returns the total development of the area.
        
        As wasteland and sea areas have no development, returns 0 in those cases.
        """
        return sum(province.development for province in self)

    @property
    def base_tax(self):
        """The total base tax of the area."""
        return sum(province.base_tax for province in self)

    @property
    def base_production(self):
        """The total base production of the area."""
        return sum(province.base_production for province in self)

    @property
    def base_manpower(self):
        """The total base manpower of the area."""
        return sum(province.base_manpower for province in self)

    @property
    def tax_income(self):
        """The monthly tax income of the area in ducats."""
        annual_income = sum(province.base_tax * 0.5 * province.autonomy_modifier for province in self)
        return round(annual_income, 2)

    @property
    def base_production_income(self):
        """The monthly production income of the area before applying the trade good price."""
        annual_income = sum(province.goods_produced * province.autonomy_modifier for province in self)
        return round(annual_income, 2)

    @property
    def goods_produced(self):
        """The amount of goods produced by the area. Is based on the province's `base_production`."""
        return round(sum(province.goods_produced for province in self), 2)

    @property
    def trade_power(self):
        """The area's trade power."""
        return round(sum(province.trade_power for province in self), 2)

    @property
    def dominant_trade_good(self):
        """The dominant trade good produced in the area determined by the total goods produced."""
        return MapUtils.get_dominant_attribute(self, "trade_goods", "goods_produced")

    @property
    def dominant_culture(self):
        """The dominant culture in the area determined by the number of provinces."""
        return MapUtils.get_dominant_attribute(self, "culture")

    @property
    def dominant_religion(self):
        """The dominant religion in the area determined by the number of provinces."""
        return MapUtils.get_dominant_attribute(self, "religion")

    @property
    def is_land_area(self):
        """Checks if the area contains any land provinces. An area can only contain one type
            of province"""
        return any(
            province.province_type == ProvinceType.NATIVE or 
            province.province_type == ProvinceType.OWNED for province in self)

    @property
    def is_sea_area(self):
        """Checks if the area contains any sea provinces. An area can only contain one type
            of province"""
        return any(province.province_type == ProvinceType.SEA for province in self)

    @property
    def is_wasteland_area(self):
        """Checks if the area contains any wasteland provinces. An area can only contain one type
            of province."""
        return any(province.province_type == ProvinceType.WASTELAND for province in self)

    def __iter__(self):
        for province in self.provinces.values():
            yield province

    def __str__(self):
        return f"The area: {self.name} (internal id: {self.area_id}), containing the provinces: {self.provinces}"
