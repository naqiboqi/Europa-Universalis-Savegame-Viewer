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