from dataclasses import dataclass

from . import EUArea



@dataclass
class EURegion:
    region_id: str
    name: str
    areas: dict[str, EUArea]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @classmethod
    def name_from_id(cls, region_id: str):
        name_split = region_id.removesuffix("region").replace("_", " ").split()
        return " ".join(name.capitalize() for name in name_split)

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

        return min_x, max_x, min_y, max_y

    @property
    def is_land_region(self):
        return any(area.is_land_area for area in self)

    @property
    def is_sea_region(self):
        return any(area.is_sea_area for area in self)

    @property
    def pixel_locations(self):
        return set(loc for area in self for loc in area.pixel_locations)

    def __iter__(self):
        for area in self.areas.values():
            yield area

    def __str__(self):
        return f"The region {self.name}, containing the areas {self.areas}"