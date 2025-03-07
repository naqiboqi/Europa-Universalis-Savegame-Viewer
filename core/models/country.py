from dataclasses import dataclass
from typing import Optional



@dataclass
class EUCountry:
    tag: str
    tag_color: tuple[int]
    name: Optional[str] = None

    def __str__(self):
        return f"The country of {self.name} (TAG: {self.tag})"
