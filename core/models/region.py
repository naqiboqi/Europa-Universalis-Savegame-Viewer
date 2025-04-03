"""
This module defines EURegion, which represents a collection of areas in Europa Universalis IV.
"""



from dataclasses import dataclass, field
from typing import Optional

from . import EUMapEntity, EUArea
from ..utils import MapUtils



@dataclass
class EURegion(EUMapEntity):
    """Represents a region on the map.

    Inherits attributes from `EUMapEntity`.
    
    Attributes:
        region_id (str): The regions's in-game identifier.
        areas (dict[str, EUArea]): A mapping of area IDs to EUAreas
            that belong to the region.

        pixel_locations (set[tuple[int, int]]): The set of (x, y) coordinates occupied by the entity.
    """
    region_id: str
    areas: dict[str, EUArea]

    pixel_locations: Optional[set[tuple[int, int]]] = field(init=False)

    def __post_init__(self):
        """Aggregate pixel locations from the contained areas."""
        self.pixel_locations = set(loc for area in self.areas.values() for loc in area.pixel_locations)
        super().__post_init__()

    @classmethod
    def from_dict(cls, data: dict):
        """Builds the region from a dictionary."""
        return cls(**data)

    @classmethod
    def name_from_id(cls, region_id: str):
        """Gets the region name from the region ID for displaying.
        
        Args:
            region_id (str): The region ID.

        Returns:
            str: The display name.
        """
        name_split = region_id.removesuffix("region").replace("_", " ").split()
        return " ".join(name.capitalize() for name in name_split)

    @property
    def development(self):
        """Returns the total development of the region.
        
        As wasteland and sea regions have no development, returns 0 in those cases.
        """
        return sum(area.development for area in self)

    @property
    def base_tax(self):
        """The total base tax of the region."""
        return sum(area.base_tax for area in self)

    @property
    def base_production(self):
        """The total base production of the region."""
        return sum(area.base_production for area in self)

    @property
    def base_manpower(self):
        """The total base manpower of the region."""
        return sum(area.base_manpower for area in self)

    @property
    def tax_income(self):
        """The monthly tax income of the region in ducats."""
        annual_income = sum(area.tax_income for area in self)
        return round(annual_income, 2)

    @property
    def base_production_income(self):
        """The monthly production income of the region before applying the trade good price."""
        annual_income = sum(area.base_production_income for area in self)
        return round(annual_income, 2)

    @property
    def goods_produced(self):
        """The amount of goods produced by the region. Is based on the province's `base_production`."""
        return round(sum(area.goods_produced for area in self), 2)

    @property
    def trade_power(self):
        """The regions's trade power."""
        return round(sum(area.trade_power for area in self), 2)

    @property
    def dominant_culture(self):
        """The dominant culture in the region determined by the number of provinces."""
        return MapUtils.get_dominant_attribute(self.provinces, "culture")

    @property
    def dominant_religion(self):
        """The dominant religion in the region determined by the number of provinces."""
        return MapUtils.get_dominant_attribute(self.provinces, "religion")

    @property
    def dominant_trade_good(self):
        """The dominant trade good produced in the region determined by the total goods produced."""
        return MapUtils.get_dominant_attribute(self.provinces, "trade_goods", "goods_produced")

    @property
    def is_land_region(self):
        """Checks if the region contains any land areas. A region can only contain one type
            of province"""
        return any(area.is_land_area for area in self)

    @property
    def is_sea_region(self):
        """Checks if the region contains any sea areas. Aregion only contain one type
            of province"""
        return any(area.is_sea_area for area in self)

    @property
    def provinces(self):
        """The provinces in the region."""
        return [province for area in self for province in area]

    def __iter__(self):
        for area in self.areas.values():
            yield area

    def __str__(self):
        return f"The region {self.name}, containing the areas {self.areas}"
