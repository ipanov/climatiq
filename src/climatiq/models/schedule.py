"""Schedule domain models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Season(str, Enum):
    """Seasons for setpoint scheduling."""

    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"

    @classmethod
    def from_month(cls, month: int) -> Season:
        """Determine season from month number (1-12).

        Uses Northern Hemisphere continental climate defaults.
        Override in configuration for Southern Hemisphere.
        """
        if month in (12, 1, 2):
            return cls.WINTER
        elif month in (3, 4, 5):
            return cls.SPRING
        elif month in (6, 7, 8):
            return cls.SUMMER
        else:
            return cls.AUTUMN


class TimePeriod(str, Enum):
    """Time-of-day periods for setpoint adjustments."""

    DEEP_NIGHT = "deep_night"  # 00:00-05:59
    MORNING = "morning"  # 06:00-08:59
    LATE_MORNING = "late_morning"  # 09:00-11:59
    EARLY_AFTERNOON = "early_afternoon"  # 12:00-14:59
    LATE_AFTERNOON = "late_afternoon"  # 15:00-17:59
    EVENING = "evening"  # 18:00-20:59
    NIGHT = "night"  # 21:00-23:59

    @classmethod
    def from_hour(cls, hour: int) -> TimePeriod:
        """Determine time period from hour (0-23)."""
        if hour < 6:
            return cls.DEEP_NIGHT
        elif hour < 9:
            return cls.MORNING
        elif hour < 12:
            return cls.LATE_MORNING
        elif hour < 15:
            return cls.EARLY_AFTERNOON
        elif hour < 18:
            return cls.LATE_AFTERNOON
        elif hour < 21:
            return cls.EVENING
        else:
            return cls.NIGHT

    @property
    def is_sleep(self) -> bool:
        """Whether this period is typically a sleep period."""
        return self in (TimePeriod.DEEP_NIGHT, TimePeriod.NIGHT)


class ScheduleEntry(BaseModel):
    """A schedule entry defining comfort targets for a specific season and time period."""

    season: Season
    period: TimePeriod
    temperature_target: float = Field(..., ge=10, le=35, description="Target temperature (°C)")
    humidity_target: float = Field(default=45.0, ge=20, le=70, description="Target humidity (%)")
    humidity_min: float = Field(default=25.0, ge=0, le=100)
    humidity_max: float = Field(default=60.0, ge=0, le=100)
