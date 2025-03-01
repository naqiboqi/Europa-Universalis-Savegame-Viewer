from core.models import EUProvince



class EUArea:
    def __init__(self, name: str, provinces: dict[int, EUProvince]|list[int]):
        self.name = name
        self.provinces = provinces

    def __str__(self):
        return f"Area: {self.name} containing provinces: {self.provinces}"