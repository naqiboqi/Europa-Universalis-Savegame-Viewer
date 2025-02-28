


class EUProvince:
    def __init__(self, prov_id: int, name: str):
        self.prov_id = prov_id
        self.name = name

    def __str__(self):
        return f"Province: {self.name} with ID {self.prov_id}"