"""
This module defines EUTradeNode, which represents a collection of provinces that contribute to trade in Europa Universalis IV.
"""


from dataclasses import dataclass, field
from enum import Enum
from math import floor
from typing import Optional

from .import EUMapEntity, EUProvince


@dataclass
class EUTradeNode(EUMapEntity):
    trade_node_id: str
    provinces: dict[int, EUProvince]

    pixel_locations: Optional[set[tuple[int, int]]] = field(init=False)

    def __post_init__(self):
        """Aggregate pixel locations from the contained provinces."""
        self.pixel_locations = set(loc for province in self.provinces.values() for loc in province.pixel_locations)
        super().__post_init__()

    @property
    def trade_power(self):
        """The total trade power of the node."""
        return round(sum(province.trade_power for province in self), 2)

    @property
    def tax_income(self) -> float:
        """The monthly tax income of the trade node in ducats."""
        pass

    @property
    def base_production_income(self) -> float:
        """The monthly production income of the trade node before applying the trade good price."""
        pass

    @property
    def development(self) -> int:
        """Returns the total development of the trade node."""
        pass

    @property
    def goods_produced(self) -> float:
        """The amount of goods produced by the trade node."""
        pass

    def __iter__(self):
        for province in self.provinces.values():
            yield province