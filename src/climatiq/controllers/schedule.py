"""Schedule controller for time-of-day comfort targets.

Provides target temperature and humidity values based on the current
season and time period. Targets follow ASHRAE 55 recommendations with
adjustments for sleep periods and morning boost.
"""

from __future__ import annotations

from climatiq.models.schedule import ScheduleEntry, Season, TimePeriod


# Default ASHRAE 55-based schedule
DEFAULT_SCHEDULE: list[ScheduleEntry] = [
    # Winter
    ScheduleEntry(season=Season.WINTER, period=TimePeriod.DEEP_NIGHT, temperature_target=20.0, humidity_target=40.0),
    ScheduleEntry(season=Season.WINTER, period=TimePeriod.MORNING, temperature_target=22.0, humidity_target=40.0),
    ScheduleEntry(season=Season.WINTER, period=TimePeriod.LATE_MORNING, temperature_target=21.0, humidity_target=35.0),
    ScheduleEntry(season=Season.WINTER, period=TimePeriod.EARLY_AFTERNOON, temperature_target=21.0, humidity_target=35.0),
    ScheduleEntry(season=Season.WINTER, period=TimePeriod.LATE_AFTERNOON, temperature_target=21.0, humidity_target=35.0),
    ScheduleEntry(season=Season.WINTER, period=TimePeriod.EVENING, temperature_target=22.0, humidity_target=40.0),
    ScheduleEntry(season=Season.WINTER, period=TimePeriod.NIGHT, temperature_target=20.0, humidity_target=40.0),
    # Summer
    ScheduleEntry(season=Season.SUMMER, period=TimePeriod.DEEP_NIGHT, temperature_target=23.0, humidity_target=50.0),
    ScheduleEntry(season=Season.SUMMER, period=TimePeriod.MORNING, temperature_target=24.0, humidity_target=45.0),
    ScheduleEntry(season=Season.SUMMER, period=TimePeriod.LATE_MORNING, temperature_target=25.0, humidity_target=45.0),
    ScheduleEntry(season=Season.SUMMER, period=TimePeriod.EARLY_AFTERNOON, temperature_target=25.0, humidity_target=45.0),
    ScheduleEntry(season=Season.SUMMER, period=TimePeriod.LATE_AFTERNOON, temperature_target=25.0, humidity_target=45.0),
    ScheduleEntry(season=Season.SUMMER, period=TimePeriod.EVENING, temperature_target=24.0, humidity_target=50.0),
    ScheduleEntry(season=Season.SUMMER, period=TimePeriod.NIGHT, temperature_target=23.0, humidity_target=50.0),
    # Spring (transitional)
    ScheduleEntry(season=Season.SPRING, period=TimePeriod.DEEP_NIGHT, temperature_target=21.0, humidity_target=42.0),
    ScheduleEntry(season=Season.SPRING, period=TimePeriod.MORNING, temperature_target=23.0, humidity_target=42.0),
    ScheduleEntry(season=Season.SPRING, period=TimePeriod.LATE_MORNING, temperature_target=23.0, humidity_target=42.0),
    ScheduleEntry(season=Season.SPRING, period=TimePeriod.EARLY_AFTERNOON, temperature_target=23.0, humidity_target=42.0),
    ScheduleEntry(season=Season.SPRING, period=TimePeriod.LATE_AFTERNOON, temperature_target=23.0, humidity_target=42.0),
    ScheduleEntry(season=Season.SPRING, period=TimePeriod.EVENING, temperature_target=22.0, humidity_target=45.0),
    ScheduleEntry(season=Season.SPRING, period=TimePeriod.NIGHT, temperature_target=21.0, humidity_target=45.0),
    # Autumn (same as spring)
    ScheduleEntry(season=Season.AUTUMN, period=TimePeriod.DEEP_NIGHT, temperature_target=21.0, humidity_target=42.0),
    ScheduleEntry(season=Season.AUTUMN, period=TimePeriod.MORNING, temperature_target=23.0, humidity_target=42.0),
    ScheduleEntry(season=Season.AUTUMN, period=TimePeriod.LATE_MORNING, temperature_target=23.0, humidity_target=42.0),
    ScheduleEntry(season=Season.AUTUMN, period=TimePeriod.EARLY_AFTERNOON, temperature_target=23.0, humidity_target=42.0),
    ScheduleEntry(season=Season.AUTUMN, period=TimePeriod.LATE_AFTERNOON, temperature_target=23.0, humidity_target=42.0),
    ScheduleEntry(season=Season.AUTUMN, period=TimePeriod.EVENING, temperature_target=22.0, humidity_target=45.0),
    ScheduleEntry(season=Season.AUTUMN, period=TimePeriod.NIGHT, temperature_target=21.0, humidity_target=45.0),
]


class ScheduleController:
    """Provides time-based comfort targets.

    Looks up the appropriate ScheduleEntry based on the current season
    and time period. Custom schedules can be provided to override defaults.
    """

    def __init__(self, schedule: list[ScheduleEntry] | None = None) -> None:
        entries = schedule or DEFAULT_SCHEDULE
        self._schedule: dict[tuple[Season, TimePeriod], ScheduleEntry] = {
            (e.season, e.period): e for e in entries
        }

    def get_target(self, season: Season, period: TimePeriod) -> ScheduleEntry:
        """Get the schedule entry for a given season and time period.

        Falls back to a sensible default if no entry is found.
        """
        entry = self._schedule.get((season, period))
        if entry is not None:
            return entry
        # Fallback: neutral comfort target
        return ScheduleEntry(season=season, period=period, temperature_target=23.0, humidity_target=45.0)

    def get_current_target(self, month: int, hour: int) -> ScheduleEntry:
        """Get the current target based on month and hour.

        Convenience method that resolves season and period automatically.
        """
        season = Season.from_month(month)
        period = TimePeriod.from_hour(hour)
        return self.get_target(season, period)
