"""
This module defines EUCountry, which represents a country in
Europa Universalis IV.
"""


import re

from dataclasses import dataclass, field
from typing import Optional, get_type_hints
from ..utils import resolve_type



@dataclass
class EUCountry:
    """Represents a country on the map.
    
    Attributes:
        tag (str): The three-letter identifier used internally by EU4 to reference the country.
        name (str): The display name of the country.
        map_color (tuple[int]): The RGB color tuple representing the country's color on the map.
        government_rank (Optional[int]): The country's government rank (default is 1).
        government_name (Optional[str]): The type or name of the country's government.
        capital_province (Optional[int]): The province ID of the country's capital.
        trade_port (Optional[int]): The province ID of the country's designated trade port.
        primary_culture (Optional[str]): The primary culture assigned to the country.
        religion (Optional[str]): The official state religion of the country.
        technology_group (Optional[str]): The technology group the country belongs to.
        technology_levels (Optional[dict[str, int]]): A dictionary holding the country's administrative,
            diplomatic, and military technology levels. Defaults to zero for all three.
        current_power_projection (Optional[float]): The current power projection value (default 0.0).
        great_power_score (Optional[float]): The country’s score used for great power ranking (default 0.0).
        prestige (Optional[float]): The prestige value of the country (default 0.0).
        stability (Optional[int]): The country's current stability level (default 0).
        legitimacy (Optional[float]): The legitimacy of the current monarchy (default 0.0).
        republican_tradition (Optional[float]): The republican tradition value (default 0.0).
        devotion (Optional[float]): The devotion value for theocratic governments (default 0.0).
        meritocracy (Optional[float]): The meritocracy value for Celestial Empire governments (default 0.0).
        subjects (Optional[set[str]]): A set of country tags representing this country’s subjects.
        allies (Optional[set[str]]): A set of country tags representing this country’s allies.
    """
    tag: str
    name: str
    map_color: tuple[int]
    government_rank: Optional[int] = 1
    government_name: Optional[str] = None
    capital_province: Optional[int] = 0
    trade_port: Optional[int] = 0

    primary_culture: Optional[str] = None
    religion: Optional[str] = None
    technology_group: Optional[str] = None
    technology_levels: Optional[dict[str, int]] = field(default_factory=lambda: {
        "adm_tech": 0,
        "dip_tech": 0,
        "mil_tech": 0
    })

    current_power_projection: Optional[float] = 0.00
    great_power_score: Optional[float] = 0.00
    prestige: Optional[float] = 0.00
    stability: Optional[int] = 0
    legitimacy: Optional[float] = 0.00
    republican_tradition: Optional[float] = 0.00
    devotion: Optional[float] = 0.00
    meritocracy: Optional[float] = 0.00

    subjects: Optional[set[str]] = None
    allies: Optional[set[str]] = None

    @staticmethod
    def fix_name(country_name: str):
        """Attempts to apply proper capitalization to the country's name."""
        name = country_name.replace('countries/', '')
        formatted_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return formatted_name.title()

    @classmethod
    def from_dict(cls, data: dict):
        """Builds the country from a dictionary."""
        converted_data = {"name": data.get("name") or data.get("tag")}
        type_hints = get_type_hints(cls)

        for key, value in data.items():
            if key not in type_hints:
                continue

            field_type = resolve_type(type_hints[key])
            try:
                if field_type == str:
                    converted_data[key] = value
                elif field_type == int:
                    converted_data[key] = int(float(value))
                elif field_type == float:
                    converted_data[key] = round(float(value), 2)
                else:
                    converted_data[key] = value
            except (ValueError, TypeError) as e:
                print(f"Error converting {key} with value {value}: {e}")

        return cls(**converted_data)

    def update_from_dict(self, data: dict):
        """Updates the country based on data from a dictionary."""
        type_hints = get_type_hints(self)

        for key, value in data.items():
            if key not in type_hints:
                continue

            field_type = resolve_type(type_hints[key])
            try:
                if field_type == str:
                    setattr(self, key, value)
                elif field_type == int:
                    setattr(self, key, int(float(value)))
                elif field_type == float:
                    setattr(self, key, round(float(value), 2))
                else:
                    setattr(self, key, value)
            except (ValueError, TypeError) as e:
                print(f"Error converting {key} with value {value}: {e}")

        return self

    def __str__(self):
        return f"The country of {self.name} (TAG: {self.tag})"
