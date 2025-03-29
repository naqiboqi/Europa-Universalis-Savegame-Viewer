"""
This module defines Terrain, an enum which represents the terrain types of a province in 
Europa Universalis IV.
"""


from enum import Enum



class TerrainType(Enum):
    """Enum of possible terrain types for a province.
    
    
    """
    GRASSLANDS = "grasslands"
    FARMLANDS = "farmlands"
    HILLS = "hills"
    MOUNTAINS = "mountains"
    FOREST = "forest"
    JUNGLE = "jungle"
    DESERT = "desert"
    DRYLANDS = "drylands"
    STEPPE = "steppe"
    MARSH = "marsh"
    COASTAL = "coastal"
    TUNDRA = "tundra"
    GLACIER = "glacier"
