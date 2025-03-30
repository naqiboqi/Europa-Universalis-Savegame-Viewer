"""
This module defines EUArea, which represents a collection of provinces in Europa Universalis IV.
"""



from dataclasses import dataclass

from . import EUProvince, ProvinceType



@dataclass
class EUArea:
    """Represents an area on the map.
    
    Attributes:
        area_id (str): The area's in-game identifier.
        name (str): The area's name.
        provinces (dict[int, EUProvince]): A mapping of province IDs to EUProvinces
            that belong to the area.
    """
    area_id: str
    name: str
    provinces: dict[int, EUProvince]

    @classmethod
    def from_dict(cls, data: dict[str, str|dict]):
        """Builds the area from a dictionary."""
        return cls(**data)

    @classmethod
    def name_from_id(cls, area_id: str):
        """Gets the area name from the area ID for displaying.
        
        Args:
            area_id (str): The area ID.

        Returns:
            str: The display name.
        """
        name_split = area_id.removesuffix("area").replace("_", " ").split()
        return " ".join(name.capitalize() for name in name_split)

    @property
    def area_km2(self):
        """Returns the estimated area of the area in square kilometers 
            using the total world map size and its pixel resolution.
        """
        world_area_km2 = 510_100_100
        map_width, map_height = 5632, 2304
        scale_factor = world_area_km2 / (map_width * map_height)

        return round(len(self.pixel_locations) * scale_factor, 2)

    @property
    def bounding_box(self):
        """Gets the bounding box for the area.
        
        The bounding box is defined as the inclusive limits of its x and y values, by
        checking its contained provinces.
        
        Returns:
            tuple[int]: The bounding box.
        """
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
    def development(self):
        """Returns the total development of the area.
        
        As wasteland and sea areas have no development, returns 0 in those cases.
        """
        return sum(province.development for province in self)

    @property
    def base_tax(self):
        """The total base tax of the area."""
        return sum(province.base_tax for province in self)

    @property
    def base_production(self):
        """The total base production of the area."""
        return sum(province.base_production for province in self)

    @property
    def base_manpower(self):
        """The total base manpower of the area."""
        return sum(province.base_manpower for province in self)

    @property
    def tax_income(self):
        """The monthly tax income of the area in ducats."""
        annual_income = sum(province.base_tax * 0.5 * province.autonomy_modifier for province in self)
        return round(annual_income, 2)

    @property
    def base_production_income(self):
        """The monthly production income of the area before applying the trade good price."""
        annual_income = sum(province.goods_produced * province.autonomy_modifier for province in self)
        return round(annual_income, 2)

    @property
    def income(self):
        """The total monthly income of the area in ducats."""
        return self.tax_income + self.base_production_income

    @property
    def goods_produced(self):
        """The amount of goods produced by the area. Is based on the province's `base_production`."""
        return round(sum(province.goods_produced for province in self), 2)

    @property
    def dominant_trade_good(self):
        """Returns the trade good with the highest total goods produced in the area."""
        trade_goods: dict[str, float] = {}

        for province in self:
            trade_good = province.trade_goods
            if not trade_good:
                continue

            if trade_good in trade_goods:
                trade_goods[trade_good] += province.goods_produced
            else:
                trade_goods[trade_good] = province.goods_produced

        if trade_goods:
            return max(trade_goods, key=trade_goods.get)
        return None

    @property
    def trade_power(self):
        """The area's trade power."""
        return round(sum(province.trade_power for province in self), 2)

    @property
    def is_land_area(self):
        """Checks if the area contains any land provinces. An area can only contain one type
            of province"""
        return any(
            province.province_type == ProvinceType.NATIVE or 
            province.province_type == ProvinceType.OWNED for province in self)

    @property
    def is_sea_area(self):
        """Checks if the area contains any sea provinces. An area can only contain one type
            of province"""
        return any(province.province_type == ProvinceType.SEA for province in self)

    @property
    def is_wasteland_area(self):
        """Checks if the area contains any wasteland provinces. An area can only contain one type
            of province."""
        return any(province.province_type == ProvinceType.WASTELAND for province in self)

    @property
    def pixel_locations(self):
        """Returns the set of x, y coordinates occupied by the area."""
        return set(loc for province in self for loc in province.pixel_locations)

    def __iter__(self):
        for province in self.provinces.values():
            yield province

    def __str__(self):
        return f"The area: {self.name} (internal id: {self.area_id}), containing the provinces: {self.provinces}"
