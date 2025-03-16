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

    @classmethod
    def name_from_id(cls, area_id: str):
        name_split = area_id.removesuffix("area").replace("_", " ").split()
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

    @property
    def pixel_locations(self):
        return set(loc for province in self for loc in province.pixel_locations)

    def __iter__(self):
        for province in self.provinces.values():
            yield province

    def __str__(self):
        return f"The area: {self.name} (internal id: {self.area_id}), containing the provinces: {self.provinces}"