"""Home and zone domain models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class WindowOrientation(str, Enum):
    """Cardinal and intercardinal window facing directions."""

    NORTH = "north"
    NORTHEAST = "northeast"
    EAST = "east"
    SOUTHEAST = "southeast"
    SOUTH = "south"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"

    @property
    def degrees(self) -> float:
        """Convert orientation to degrees from North (clockwise)."""
        mapping = {
            "north": 0.0,
            "northeast": 45.0,
            "east": 90.0,
            "southeast": 135.0,
            "south": 180.0,
            "southwest": 225.0,
            "west": 270.0,
            "northwest": 315.0,
        }
        return mapping[self.value]

    @classmethod
    def from_degrees(cls, degrees: float) -> WindowOrientation:
        """Convert degrees to nearest orientation."""
        normalized = degrees % 360
        directions = [
            (0.0, cls.NORTH),
            (45.0, cls.NORTHEAST),
            (90.0, cls.EAST),
            (135.0, cls.SOUTHEAST),
            (180.0, cls.SOUTH),
            (225.0, cls.SOUTHWEST),
            (270.0, cls.WEST),
            (315.0, cls.NORTHWEST),
        ]
        closest = min(directions, key=lambda d: min(abs(normalized - d[0]), 360 - abs(normalized - d[0])))
        return closest[1]


class Zone(BaseModel):
    """A climate zone within a home (room, area, or open-plan section).

    Each zone has its own sensors, devices, and comfort targets.
    Zones are the fundamental unit of climate control.
    """

    id: str = Field(..., description="Unique zone identifier (e.g., 'living_room', 'bedroom_1')")
    name: str = Field(..., description="Human-readable zone name")
    window_bearing_deg: float | None = Field(
        default=None,
        ge=0,
        le=360,
        description="Window facing direction in degrees from North (0=N, 90=E, 180=S, 270=W). None if no window.",
    )
    area_m2: float | None = Field(default=None, gt=0, description="Zone area in square meters")
    sensor_ids: list[str] = Field(default_factory=list, description="IDs of sensors in this zone")
    device_ids: list[str] = Field(default_factory=list, description="IDs of controllable devices in this zone")

    @property
    def window_orientation(self) -> WindowOrientation | None:
        """Get window orientation as enum, if configured."""
        if self.window_bearing_deg is None:
            return None
        return WindowOrientation.from_degrees(self.window_bearing_deg)

    @property
    def has_window(self) -> bool:
        """Whether this zone has a window configured."""
        return self.window_bearing_deg is not None


class Home(BaseModel):
    """A home with multiple climate zones.

    This is the top-level configuration entity. It contains all zones,
    their relationships, and global settings like location.
    """

    name: str = Field(..., description="Home name")
    zones: list[Zone] = Field(default_factory=list, description="Climate zones in this home")
    latitude: float = Field(..., ge=-90, le=90, description="Home latitude for weather/solar calculations")
    longitude: float = Field(..., ge=-180, le=180, description="Home longitude")
    timezone: str = Field(default="UTC", description="IANA timezone string (e.g., 'Europe/Skopje')")
    altitude_m: float | None = Field(default=None, description="Altitude in meters above sea level")

    def get_zone(self, zone_id: str) -> Zone | None:
        """Find a zone by its ID."""
        return next((z for z in self.zones if z.id == zone_id), None)

    @property
    def zone_ids(self) -> list[str]:
        """List of all zone IDs."""
        return [z.id for z in self.zones]
