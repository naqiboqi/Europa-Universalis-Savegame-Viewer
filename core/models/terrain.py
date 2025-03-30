"""
This module defines Terrain, an enum which represents the terrain types of a province in 
Europa Universalis IV.
"""


from enum import Enum



class TerrainType(Enum):
    """Enum of possible terrain types for a province."""

    GRASSLANDS = "grasslands"
    """Flat and fertile land with low development cost, easy movement, and fast construction."""

    FARMLANDS = "farmlands"
    """The most developed and fertile terrain, with the lowest development cost and fastest construction speed."""

    HILLS = "hills"
    """Rough terrain that increases development cost and slows movement, but provides defensive bonuses."""

    MOUNTAINS = "mountains"
    """The most difficult terrain to develop, with very high development cost and movement penalties, but excellent defensive advantages."""

    FOREST = "forest"
    """Moderately increases development cost and slows movement due to dense tree cover."""

    JUNGLE = "jungle"
    """Harsh terrain with high development cost and severe movement penalties, making construction difficult."""

    DESERT = "desert"
    """Arid and barren land with high development cost, reduced supply limit, and slow construction speed."""

    DRYLANDS = "drylands"
    """Semi-arid terrain with moderate development cost and fewer penalties than deserts."""

    STEPPE = "steppe"
    """Open grasslands with low development cost but little natural defense, favoring cavalry movement."""

    MARSH = "marsh"
    """Difficult terrain to develop, with high development cost, slow construction, and severe movement penalties."""

    COASTAL = "coastal"
    """Provides access to naval trade and shipbuilding but has little impact on development cost or movement."""

    TUNDRA = "tundra"
    """Cold and infertile land with high development cost and slow construction, similar to drylands but harsher."""

    GLACIER = "glacier"
    """Extremely harsh and nearly uninhabitable, with the highest development cost and severe movement penalties."""

    @property
    def __str__(self):
        return self.value.capitalize().replace("_", " ")

    @classmethod
    def from_str(cls, value: str):
        """Returns the string value of the map mode."""
        try:
            return cls[value.upper()]
        except KeyError:
            return ""
