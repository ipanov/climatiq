"""Tests for schedule controller."""

from climatiq.controllers.schedule import ScheduleController
from climatiq.models.schedule import Season, TimePeriod


class TestScheduleController:
    """Tests for ScheduleController."""

    def test_default_schedule_has_all_combinations(self) -> None:
        """Default schedule should cover all season x period combinations."""
        controller = ScheduleController()
        for season in Season:
            for period in TimePeriod:
                entry = controller.get_target(season, period)
                assert entry is not None
                assert entry.season == season
                assert entry.period == period

    def test_winter_night_is_cooler(self) -> None:
        """Winter night should target lower temperature than winter day."""
        controller = ScheduleController()
        night = controller.get_target(Season.WINTER, TimePeriod.DEEP_NIGHT)
        day = controller.get_target(Season.WINTER, TimePeriod.LATE_MORNING)
        assert night.temperature_target < day.temperature_target

    def test_summer_is_warmer_than_winter(self) -> None:
        """Summer targets should be warmer than winter targets for same period."""
        controller = ScheduleController()
        summer = controller.get_target(Season.SUMMER, TimePeriod.LATE_MORNING)
        winter = controller.get_target(Season.WINTER, TimePeriod.LATE_MORNING)
        assert summer.temperature_target > winter.temperature_target

    def test_get_current_target(self) -> None:
        """Should resolve month and hour to correct season and period."""
        controller = ScheduleController()
        # January at 3am = winter, deep_night
        entry = controller.get_current_target(month=1, hour=3)
        assert entry.season == Season.WINTER
        assert entry.period == TimePeriod.DEEP_NIGHT

        # July at 14:00 = summer, early_afternoon
        entry = controller.get_current_target(month=7, hour=14)
        assert entry.season == Season.SUMMER
        assert entry.period == TimePeriod.EARLY_AFTERNOON

    def test_custom_schedule(self) -> None:
        """Custom schedule entries should override defaults."""
        from climatiq.models.schedule import ScheduleEntry

        custom = [
            ScheduleEntry(season=Season.SUMMER, period=TimePeriod.MORNING, temperature_target=18.0)
        ]
        controller = ScheduleController(schedule=custom)
        entry = controller.get_target(Season.SUMMER, TimePeriod.MORNING)
        assert entry.temperature_target == 18.0
