"""
This module defines EURegion, which represents a collection of areas in Europa Universalis IV.
"""



from dataclasses import dataclass

from . import EUArea



@dataclass
class EURegion:
    """Represents a region on the map.
    
    Attributes:
        region_id (str): The regions's in-game identifier.
        name (str): The regions's name.
        areas (dict[str, EUArea]): A mapping of area IDs to EUAreas
            that belong to the region.
    """
    region_id: str
    name: str
    areas: dict[str, EUArea]

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
    def area_km2(self):
        """Returns the estimated area of the region in square kilometers 
            using the total world map size and its pixel resolution.
        """
        world_area_km2 = 510_100_100
        map_width, map_height = 5632, 2304
        scale_factor = world_area_km2 / (map_width * map_height)

        return round(len(self.pixel_locations) * scale_factor, 2)

    @property
    def bounding_box(self):
        """Gets the bounding box for the region.
        
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
    def pixel_locations(self):
        """Returns the set of x, y coordinates occupied by the region."""
        return set(loc for area in self for loc in area.pixel_locations)

    def __iter__(self):
        for area in self.areas.values():
            yield area

    def __str__(self):
        return f"The region {self.name}, containing the areas {self.areas}"