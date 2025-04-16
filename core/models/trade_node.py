"""
This module defines EUTradeNode and EUTradeNodeParticipant, used for storing information relavent to trade nodes in Europa Universalis IV.
"""

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional, get_type_hints
from . import EUMapEntity, EUProvince
from ..utils import MapUtils, resolve_type



@dataclass
class EUTradeNodeParticipant:
    """Represents a participant in a trade node.
    
    The participoting country muse have either trade power or ships in the node.
    
    Attributes:
        Attributes:
        tag (str): The country tag identifying the participant.
        trade_power (Optional[float]): The total trade power the participant exerts in the node.
        trade_power_in_node_fraction (Optional[float]): The participant's share of total trade power in the node, as a fraction.
        steered_trade_value (Optional[float]): The total trade value being steered away from the node by this participant.
        provincial_trade_power (Optional[float]): The trade power contribution from owned provinces within the node.
        num_light_ships (Optional[int]): The number of light ships assigned to protect trade in this node.
        ship_trade_power (Optional[float]): The trade power contributed by light ships.
        total_trade_income (Optional[float]): The participant's total income from this trade node.
        privateer_power (Optional[float]): The trade power contributed by privateer fleets.
        privateer_income (Optional[float]): The income earned from privateering in this node.
        has_trader (Optional[bool]): Whether the participant has a merchant assigned to the node.
        has_trade_capital (Optional[bool]): Whether the participant's trade capital is located in this node.
    """
    tag: str
    trade_power: Optional[float] = 0.00
    trade_power_in_node_fraction: Optional[float] = 0.00
    steered_trade_value: Optional[float] = 0.00
    provincial_trade_power: Optional[float] = 0.00
    num_light_ships: Optional[int] = 0
    ship_trade_power: Optional[float] = 0.00
    total_trade_income: Optional[float] = 0.00
    privateer_power: Optional[float] = 0.00
    privateer_income: Optional[float] = 0.00
    has_trader: Optional[bool] = False  
    has_trade_capital: Optional[bool] = False

    @classmethod
    def from_dict(cls, data: dict):
        """Builds the class from a dictionary."""
        if not ("val" in data or "privateer_mission" in data):
            return None

        attr_names = {
            "val": "trade_power",
            "already_sent": "steered_trade_value",
            "power_fraction": "trade_power_in_node_fraction",
            "province_power": "provencial_trade_power",
            "light_ship": "num_light_ships",
            "ship_power": "ship_trade_power",
            "money": "total_trade_income",
            "privateer_mission": "privateer_power",
            "privateer_money": "privateer_income",
            "has_trader": "has_trader",
            "has_capital": "has_trade_capital",
        }

        converted_data = {"tag": data["tag"]}
        type_hints = get_type_hints(cls)

        for raw_key, value in data.items():
            if raw_key not in attr_names:
                continue

            key = attr_names[raw_key]
            if key not in type_hints:
                continue

            field_type = resolve_type(type_hints[key])
            try:
                if field_type in [str, Optional[str]]:
                    converted_data[key] = value
                elif field_type in [int, Optional[int]]:
                    converted_data[key] = int(float(value))
                elif field_type in [float, Optional[float]]:
                    converted_data[key] = float(value)
                else:
                    converted_data[key] = value
            except (ValueError, TypeError) as e:
                print(f"Error converting {key} with value {value}: {e}")

        return cls(**converted_data)

    @property
    def has_merchant_in_node(self):
        """If the country has a merchant in the current node."""
        return "Yes" if self.has_trader else "No"

    @property
    def node_merchant_mission(self):
        """The merchant's current mission in the node. Can either collect income or steer it to an adjencent node."""
        if self.has_trade_capital or self.total_trade_income:
            return "Collects"

        return "Steers Trade"

@dataclass
class EUTradeNode(EUMapEntity):
    """Represents a trade node on the map.
    
    A trade node is a collection of provinces and countries that contribute and exchange trade goods locally.
    
    Inherits attributes from `EUMapEntity`.

    Attributes:
        origin_number (int): Unique integer identifier for the node's origin.
        trade_node_id (str): String ID representing the trade node's internal name.
        provinces (dict[int, EUProvince]): Mapping of province IDs to their corresponding province objects within the trade node.
        incoming_nodes (list[dict[str, str]]): List of dictionaries detailing incoming trade connections from other nodes.
        top_countries (OrderedDict[str, float]): An ordered mapping of country tags to their trade power, sorted descending.
        node_participants (list[EUTradeNodeParticipant]): List of countries actively participating in this trade node.

        total_trade_value (Optional[float]): Total trade value present in the node, including both retained and outgoing amounts.
        local_trade_value (Optional[float]): Portion of trade value retained locally in the node.
        total_trade_power (Optional[float]): Sum of trade power exerted by all participants in the node.
        provencial_trade_power (Optional[float]): Trade power contributed directly by provinces.
        outgoing_trade_value (Optional[float]): Portion of the node's trade value that is being transferred to downstream nodes.
        added_outgoing_trade_value (Optional[float]): Additional trade value being pushed out after modifiers.
        trade_value_retention (Optional[float]): Percentage of trade value retained versus sent outward.

        num_collectors (Optional[int]): Number of merchants actively collecting trade from this node.
        num_collectors_including_pirates (Optional[float]): Number of collectors, including privateers or piracy effects.
        collectors_trade_power (Optional[float]): Total trade power from active collectors.
        collectors_trade_power_including_pirates (Optional[float]): Total collector trade power, factoring in piracy.
        retained_trade_power (Optional[float]): Trade power portion effectively securing retained trade value.
        highest_trade_power (Optional[float]): The single highest trade power held by a country in this node.
        pulled_trade_power (Optional[float]): Trade power drawn from incoming nodes.

        pixel_locations (Optional[set[tuple[int, int]]]): The set of (x, y) coordinates occupied by the trade node.
    """
    origin_number: int
    trade_node_id: str
    provinces: dict[int, EUProvince]
    incoming_nodes: list[dict[str, str]]
    top_countries: OrderedDict[str, float]
    node_participants: list[EUTradeNodeParticipant]

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
            "top_countries": data["top_countries"],
            "node_participants": data["node_participants"]
        }

        type_hints = get_type_hints(cls)

        for raw_key, value in data.items():
            if raw_key not in attr_names:
                continue

            key = attr_names[raw_key]
            if key not in type_hints:
                continue

            field_type = resolve_type(type_hints[key])
            try:
                if field_type in [str, Optional[str]]:
                    converted_data[key] = value
                elif field_type in [int, Optional[int]]:
                    converted_data[key] = int(float(value))
                elif field_type in [float, Optional[float]]:
                    converted_data[key] = round(float(value), 2)
                else:
                    converted_data[key] = value
            except (ValueError, TypeError) as e:
                print(f"Error converting {key} with value {value}: {e}")

        return cls(**converted_data)

    @property
    def incoming_value_total(self):
        """The total incoming trade value from this trade node's incoming nodes."""
        return round(sum(node["added_value"] for node in self.incoming_nodes), 2)

    @property
    def remaining_total_value(self):
        """The remaining trade value after adding the incoming value and subtracting the outgoing value."""
        return round(self.incoming_value_total + self.local_trade_value - self.outgoing_trade_value, 2)

    @property
    def num_light_ships(self):
        """The number of light ships sent by countries to protect trade in this node."""
        return sum(participant.num_light_ships for participant in self.node_participants)

    @property
    def total_light_ship_power(self):
        """The total light ship power in this trade node."""
        return sum(
            participant.ship_trade_power or 0.00 for participant in self
            if participant.privateer_power == 0)

    @property
    def total_privateer_power(self):
        """The total privateer power in this trade node."""
        return sum(
            participant.privateer_power or 0.00
            for participant in self)

    @property
    def privateer_efficiency_modifier(self):
        """The privateer efficiency modifier in this trade node.
        
        A higher modifier means that privateers are more weaker here.
        """
        light_ship_power = self.total_light_ship_power
        privateer_power = self.total_privateer_power
        if light_ship_power + privateer_power == 0:
            return 0.00

        return round((light_ship_power / (light_ship_power + privateer_power)) * 100, 2)

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
        for participant in self.node_participants:
            yield participant
