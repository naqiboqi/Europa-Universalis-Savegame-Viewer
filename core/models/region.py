from dataclasses import dataclass

from . import EUArea



@dataclass
class EURegion:
    region_id: str
    name: str
    areas: dict[str, EUArea]

    @classmethod
    def name_from_id(cls, area_id: str):
        name_split = area_id.removesuffix("region").replace("_", " ").split()
        return " ".join(name.capitalize() for name in name_split)

    def __iter__(self):
        for area in self.areas.values():
            yield area

    def __str__(self):
        return f"The region {self.name}, containing the areas {self.areas}"