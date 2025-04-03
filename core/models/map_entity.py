from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EUMapEntity(ABC):
    """
    Abstract base class representing a mappable entity on the game map.

    Attributes:
        name (str): The name of the entity.
        pixel_locations (set[tuple[int, int]]): The set of (x, y) coordinates occupied by the entity.

        border_pixels (set[tuple[int, int]]): The set of `(x, y)` tuples for the entity's border pixels.
            Border pixels are those adjacent to areas not belonging to the entity.
        bounding_box (tuple[int, int, int, int]): The bounding box as `(min_x, max_x, min_y, max_y)`,
            representing the smallest rectangle enclosing the entity.
    """
    name: str
    pixel_locations: set[tuple[int, int]]

    # Will only ever be calculated in `__post_init__()`
    border_pixels: Optional[set[tuple[int, int]]] = field(init=False)
    bounding_box: Optional[tuple[int, int, int, int]] = field(init=False)

    def __post_init__(self):
        """Calculates bounding box and border pixels."""
        self.border_pixels = self._calculate_border_pixels()
        self.bounding_box = self._calculate_bounding_box()

    def _calculate_border_pixels(self):
        """The border pixels of a province.

        Defined as pixels that are adjacent to other provinces (not in the same set).
        
        Returns:
            border (set[tuple[int, int]]): The set of `(x, y)` tuples for the border pixels.
        """
        border_pixels: set[tuple[int, int]] = set()

        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for (x, y) in self.pixel_locations:
            for dx, dy in directions:
                neighbor = (x + dx, y + dy)
                if neighbor not in self.pixel_locations:
                    border_pixels.add((x, y))
                    break

        return border_pixels

    def _calculate_bounding_box(self):
        """Gets the bounding box for the province.
        
        The bounding box is defined as the inclusive limits of its `(x, y)` pixel locations.

        Returns:
            bounds (tuple[int, int, int, int]): The bounding box as `min_x`, `max_x`, `min_y`, `max_y`.
        """
        if not self.pixel_locations:
            return None

        x_values, y_values = zip(*self.pixel_locations)
        return min(x_values), max(x_values), min(y_values), max(y_values)

    @property
    def area_km2(self):
        """Returns the area of the entity in square kilometers."""
        world_area_km2 = 510_100_100
        map_width, map_height = 5632, 2304
        scale_factor = world_area_km2 / (map_width * map_height)

        return round(len(self.pixel_locations) * scale_factor, 2)

    @property
    @abstractmethod
    def tax_income(self) -> float:
        """The monthly tax income of the entity in ducats."""
        pass

    @property
    @abstractmethod
    def base_production_income(self) -> float:
        """The monthly production income of the entity before applying the trade good price."""
        pass

    @property
    def income(self):
        """The total monthly income of the entity in ducats."""
        return self.tax_income + self.base_production_income

    @property
    @abstractmethod
    def development(self) -> int:
        """Returns the total development of the province."""
        pass
