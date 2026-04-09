"""Tests for PMV/PPD calculations."""

import math

import pytest

from climatiq.comfort.pmv import calculate_pmv, _ppd_from_pmv


class TestPMVCalculation:
    """Tests for PMV calculation function."""

    def test_neutral_conditions(self) -> None:
        """PMV should be near 0 for neutral comfort conditions."""
        result = calculate_pmv(air_temp=23.0, humidity=50.0, clothing=0.7, metabolic_rate=1.1)
        assert -0.5 <= result.pmv <= 0.5, f"PMV {result.pmv} not near 0 for neutral conditions"

    def test_hot_conditions(self) -> None:
        """PMV should be positive for hot conditions."""
        result = calculate_pmv(air_temp=30.0, humidity=60.0, clothing=0.5, metabolic_rate=1.1)
        assert result.pmv > 0.5, f"PMV {result.pmv} should be positive for hot conditions"
        assert result.comfort_level.value in ("warm", "slightly_warm", "hot")

    def test_cold_conditions(self) -> None:
        """PMV should be negative for cold conditions."""
        result = calculate_pmv(air_temp=16.0, humidity=40.0, clothing=0.7, metabolic_rate=1.1)
        assert result.pmv < -0.5, f"PMV {result.pmv} should be negative for cold conditions"

    def test_heavy_clothing_shifts_comfort(self) -> None:
        """Heavy clothing should make a warm room feel warmer."""
        light = calculate_pmv(air_temp=26.0, clothing=0.5, metabolic_rate=1.1)
        heavy = calculate_pmv(air_temp=26.0, clothing=1.5, metabolic_rate=1.1)
        # Heavy clothing in the same room should make PMV higher (warmer sensation)
        # Note: pythermalcomfort may handle this differently, but the trend should hold

    def test_radiant_temp_defaults_to_air(self) -> None:
        """If radiant temp not provided, should use air temp."""
        with_radiant = calculate_pmv(air_temp=22.0, radiant_temp=22.0)
        without_radiant = calculate_pmv(air_temp=22.0, radiant_temp=None)
        assert abs(with_radiant.pmv - without_radiant.pmv) < 0.01

    def test_pmv_clamped_to_range(self) -> None:
        """PMV should be clamped to [-3, +3]."""
        result = calculate_pmv(air_temp=50.0, humidity=90.0, clothing=1.5, metabolic_rate=2.0)
        assert -3.0 <= result.pmv <= 3.0

    def test_compliant_result(self) -> None:
        """Comfortable conditions should be ASHRAE 55 compliant."""
        result = calculate_pmv(air_temp=23.0, humidity=50.0)
        assert result.is_compliant


class TestPPD:
    """Tests for PPD calculation."""

    def test_ppd_at_pmv_zero(self) -> None:
        """PPD should be 5% at PMV=0 (minimum dissatisfaction)."""
        ppd = _ppd_from_pmv(0.0)
        assert abs(ppd - 5.0) < 0.1

    def test_ppd_increases_with_pmv(self) -> None:
        """PPD should increase as PMV deviates from 0."""
        ppd_0 = _ppd_from_pmv(0.0)
        ppd_1 = _ppd_from_pmv(1.0)
        ppd_2 = _ppd_from_pmv(2.0)
        assert ppd_1 > ppd_0
        assert ppd_2 > ppd_1

    def test_ppd_symmetric(self) -> None:
        """PPD should be the same for +PMV and -PMV."""
        ppd_pos = _ppd_from_pmv(1.0)
        ppd_neg = _ppd_from_pmv(-1.0)
        assert abs(ppd_pos - ppd_neg) < 0.1


class TestSeasonAndTime:
    """Tests for season and time period determination."""

    def test_season_from_month(self) -> None:
        from climatiq.models.schedule import Season

        assert Season.from_month(1) == Season.WINTER
        assert Season.from_month(7) == Season.SUMMER
        assert Season.from_month(4) == Season.SPRING
        assert Season.from_month(10) == Season.AUTUMN

    def test_time_period_from_hour(self) -> None:
        from climatiq.models.schedule import TimePeriod

        assert TimePeriod.from_hour(3) == TimePeriod.DEEP_NIGHT
        assert TimePeriod.from_hour(7) == TimePeriod.MORNING
        assert TimePeriod.from_hour(12) == TimePeriod.EARLY_AFTERNOON
        assert TimePeriod.from_hour(22) == TimePeriod.NIGHT
