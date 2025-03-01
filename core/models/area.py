from dataclasses import dataclass

from . import EUProvince



@dataclass
class EUArea:
    name: str
    provinces: dict[int, EUProvince]|list[int]

    def __str__(self):
        return f"The area: {self.name}, containing the provinces: {self.provinces}"