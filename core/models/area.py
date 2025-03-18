"""
This module defines EUArea, which represents a collection of provinces in Europa Universalis IV.
"""



from dataclasses import dataclass

from . import EUProvince, ProvinceType



@dataclass
class EUArea:
    """Represents an area on the map.
    
    Attributes:
        area_id (str): The area's in-game identifier.
        name (str): The area's name.
        provinces (dict[int, EUProvince]): A mapping of province IDs to EUProvinces
            that belong to the area.
    """
    area_id: str
    name: str
    provinces: dict[int, EUProvince]

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
    def bounding_box(self):
        """Gets the bounding box for the area.
        
        The bounding box is defined as the inclusive limits of its x and y values, by
        checking its contained provinces.
        
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

        return min_x, max_x, min_y, max_y

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

    @property
    def pixel_locations(self):
        """Returns the set of x, y coordinates occupied by the area."""
        return set(loc for province in self for loc in province.pixel_locations)

    def __iter__(self):
        for province in self.provinces.values():
            yield province

    def __str__(self):
        return f"The area: {self.name} (internal id: {self.area_id}), containing the provinces: {self.provinces}"
