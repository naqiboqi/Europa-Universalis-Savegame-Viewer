from dataclasses import dataclass

from . import EUProvince



@dataclass
class EUArea:
    area_id: str
    name: str
    provinces: dict[int, EUProvince]|list[int]

    @classmethod
    def name_from_id(cls, area_id: str):
        name_split = area_id.removesuffix("area").replace("_", " ").split()
        return " ".join(name.capitalize() for name in name_split)

    def __iter__(self):
        for province in self.provinces.values():
            yield province

    def __str__(self):
        return f"The area: {self.name} (internal id: {self.area_id}), containing the provinces: {self.provinces}"