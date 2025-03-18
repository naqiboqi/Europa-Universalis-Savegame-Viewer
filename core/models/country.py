"""
This module defines EUCountry, which represents a country in
Europa Universalis IV.
"""


import re

from dataclasses import dataclass
from typing import Optional



@dataclass
class EUCountry:
    """Represents a country on the map.
    
    Attributes:
        tag (str): The three-letter identifier used internally by EU4.
        tag_color (tuple[int, int, int]): The RGB color of the country.
        name (Optional[str]): The name of the country. 
            Is optional as some countries have dynamic names
            (and I am not sure how to get them from savefiles yet).
    """
    tag: str
    tag_color: tuple[int]
    name: Optional[str] = None

    @staticmethod
    def fix_name(country_name: str):
        """Attempts to apply proper capitalization to the country's name."""
        name = country_name.replace('countries/', '')
        formatted_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return formatted_name.title()

    def __str__(self):
        return f"The country of {self.name} (TAG: {self.tag})"
