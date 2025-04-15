"""
Initialization module for the Europa Universalis world components.

This module imports the necessary components for the game world, including 
provinces, countries, areas, map modes, and regions. These components are 
used to define and manage the structure of the Europa Universalis world 
and its various entities.

Imports:
    - **EUProvince**: Represents a province on the map.
    - **ProvinceType**: Enumeration of the different province types.
    - **ProvinceTypeColor**: Colors associated with different province types.
    - **EUCountry**: Represents a country in the game.
    - **EUArea**: Represents a geographical area.
    - **MapMode** Defines the different map modes.
    - **EURegion**: Represents a region, which contains multiple areas.
"""

from .map_entity import EUMapEntity
from .country import EUCountry
from .terrain import TerrainType
from .province import EUProvince, ProvinceType, ProvinceTypeColor
from .trade_node import EUTradeNode, EUTradeNodeParticipant
from .area import EUArea
from .mapmode import MapMode
from .region import EURegion

__all__ = [
    'EUMapEntity',
    'EUCountry', 
    'TerrainType',
    'EUProvince', 
    'ProvinceType', 
    'ProvinceTypeColor', 
    'EUTradeNode',
    'EUTradeNodeParticipant',
    'EUArea', 
    'MapMode', 
    'EURegion',
]