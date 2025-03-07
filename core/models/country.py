import re

from dataclasses import dataclass
from typing import Optional



@dataclass
class EUCountry:
    tag: str
    tag_color: tuple[int]
    name: Optional[str] = None

    @staticmethod
    def fix_name(country_name: str):
        name = country_name.replace('countries/', '')
        formatted_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return formatted_name.title()

    def __str__(self):
        return f"The country of {self.name} (TAG: {self.tag})"
