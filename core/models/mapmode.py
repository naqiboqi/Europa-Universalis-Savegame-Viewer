"""
This module defines a MapMode that is used for displaying and drawing the map.
"""

from enum import Enum



class MapMode(Enum):
    """Enum of map modes.
    
    - Political
    - Area
    - Region
    - Development
    - Religion
    """
    POLITICAL = "political"
    AREA = "area"
    REGION = "region"
    DEVELOPMENT = "development"
    RELIGION = "religion"

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
