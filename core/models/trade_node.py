"""
This module defines EUTradeNode, which represents a collection of provinces that contribute to trade in Europa Universalis IV.
"""

from collections import OrderedDict
from dataclasses import dataclass, field, fields
from typing import Optional

from .import EUMapEntity, EUCountry, EUProvince
from ..utils import MapUtils



@dataclass
class EUTradeNodeParticipant:
    country: EUCountry
    trade_power: float
    provincial_trade_power: Optional[float] = 0.00
    ship_trade_power: Optional[float] = 0.00
    trade_power_share_fraction: Optional[float] = 0.00
    trade_income: Optional[float] = 0.00
    has_trader: Optional[bool] = False
    has_trade_capital: Optional[bool] = False
    num_light_ships: Optional[int] = 0
    trading_policy: Optional[str] = None


@dataclass
class EUTradeNode(EUMapEntity):
    """Represents a trade node on the map.
    
    Inherits attributes from `EUMapEntity`.

    Attributes:
        origin_number (int):
        trade_node_id (str):
        provinces (dict[int, EUProvince]):
        incoming_nodes (list[dict[str, str]]):
        top_countries (OrderedDict[str, float]):

        total_trade_value (Optional[float]):
        local_trade_value (Optional[float]):
        total_trade_power (Optional[float]):
        provencial_trade_power (Optional[float]):
        outgoing_trade_value (Optional[float]):
        added_outgoing_trade_value (Optional[float]):
        trade_value_retention (Optional[float]):
        num_collectors (Optional[int]):
        num_collectors_including_pirates (Optional[float]):
        collectors_trade_power (Optional[float]):
        collectors_trade_power_including_pirates (Optional[float]):
        retained_trade_power (Optional[float]):
        highest_trade_power (Optional[float]):
        pulled_trade_power (Optional[float]):

        pixel_locations (Optional[set[tuple[int, int]]]):
    """
    origin_number: int
    trade_node_id: str
    provinces: dict[int, EUProvince]
    incoming_nodes: list[dict[str, str]]
    top_countries: OrderedDict[str, float]

    total_trade_value: Optional[float] = 0.00
    local_trade_value: Optional[float] = 0.00
    total_trade_power: Optional[float] = 0.00
    provencial_trade_power: Optional[float] = 0.00
    outgoing_trade_value: Optional[float] = 0.00
    added_outgoing_trade_value: Optional[float] = 0.00
    trade_value_retention: Optional[float] = 0.00
    num_collectors: Optional[int] = 0
    num_collectors_including_pirates: Optional[float] = 0
    collectors_trade_power: Optional[float] = 0.00
    collectors_trade_power_including_pirates: Optional[float] = 0.00
    retained_trade_power: Optional[float] = 0.00
    highest_trade_power: Optional[float] = 0.00
    pulled_trade_power: Optional[float] = 0.00

    pixel_locations: Optional[set[tuple[int, int]]] = field(init=False)

    def __post_init__(self):
        """Aggregate pixel locations from the contained provinces."""
        self.pixel_locations = set(
            loc for province in self.provinces.values()
            for loc in province.pixel_locations)

        super().__post_init__()

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        """Builds the trade node from a dictionary."""
        attr_names = {
            "origin_number": "origin_number",
            "trade_node_id": "trade_node_id",
            "current": "total_trade_value",
            "local_value": "local_trade_value",
            "outgoing": "outgoing_trade_value",
            "added_outgoing": "added_outgoing_trade_value",
            "retention": "trade_value_retention",
            "num_collectors": "num_collectors",
            "num_collectors_including_pirates": "num_collectors_including_pirates",
            "total": "total_trade_power",
            "p_pow": "provencial_trade_power",
            "collector_power": "collectors_trade_power",
            "collector_power_including_pirates": "collectors_trade_power_including_pirates",
            "retain_power": "retained_trade_power",
            "highest_power": "highest_trade_power",
            "pull_power": "pulled_trade_power",
        }

        converted_data = {
            "name": MapUtils.format_name(data["trade_node_id"]), 
            "provinces": data["provinces"],
            "incoming_nodes": data["incoming_nodes"],
            "top_countries": data["top_countries"]}
        field_types = {f.name: f.type for f in fields(cls)}

        for raw_key, value in data.items():
            if raw_key not in attr_names:
                continue

            key = attr_names[raw_key]
            if key not in field_types:
                continue

            field_type = field_types[key]
            try:
                if field_type in ["str", "Optional[str]"]:
                    converted_data[key] = value
                elif field_type in ["int", "Optional[int]"]:
                    converted_data[key] = int(float(value))
                elif field_type in ["float", "Optional[float]"]:
                    converted_data[key] = float(value)
                else:
                    converted_data[key] = value
            except (ValueError, TypeError) as e:
                print(f"Error converting {key} with value {value}: {e}")

        return cls(**converted_data)

    @property
    def pulled_trade_value(self):
        """The monthly amount of trade value pulled from the trade node."""
        return round((1 - self.retained_trade_power) * self.total_trade_value, 2)

    @property
    def tax_income(self) -> float:
        """The monthly tax income of the trade node in ducats."""
        return 0.00

    @property
    def base_production_income(self) -> float:
        """The monthly production income of the trade node before applying the trade good price."""
        return 0.00

    @property
    def development(self) -> int:
        """Returns the total development of the trade node."""
        return 0.00

    @property
    def goods_produced(self) -> float:
        """The amount of goods produced by the trade node."""
        return 0.00

    def __iter__(self):
        for province in self.provinces.values():
            yield province