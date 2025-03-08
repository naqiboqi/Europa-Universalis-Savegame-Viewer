from dataclasses import dataclass

from . import EUProvince, ProvinceType



@dataclass
class EUArea:
    area_id: str
    name: str
    provinces: dict[int, EUProvince]|list[int]

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        return cls(**data)

    @property
    def is_land_area(self):
        return any(
            province.province_type == ProvinceType.NATIVE or 
            province.province_type == ProvinceType.OWNED for province in self)

    @property
    def is_sea_area(self):
        return any(province.province_type == ProvinceType.SEA for province in self)

    @property
    def is_wasteland_area(self):
        return any(province.province_type == ProvinceType.WASTELAND for province in self)

    @classmethod
    def name_from_id(cls, area_id: str):
        name_split = area_id.removesuffix("area").replace("_", " ").split()
        return " ".join(name.capitalize() for name in name_split)

    @property
    def pixel_locations(self):
        return set(loc for province in self for loc in province.pixel_locations)

    def __iter__(self):
        for province in self.provinces.values():
            yield province

    def __str__(self):
        return f"The area: {self.name} (internal id: {self.area_id}), containing the provinces: {self.provinces}"