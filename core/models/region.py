from dataclasses import dataclass

from . import EUArea



@dataclass
class EURegion:
    region_id: str
    name: str
    areas: dict[str, EUArea]

    def __str__(self):
        return f"The region {self.name}, containing the areas {self.areas}"