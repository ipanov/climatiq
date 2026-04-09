"""Tests for dew point calculation."""

import math

import pytest

from climatiq.comfort.dew_point import calculate_dew_point, is_condensation_risk


class TestDewPoint:
    """Tests for Magnus formula dew point calculation."""

    def test_known_values(self) -> None:
        """Test against known dew point values."""
        # At 50% RH and 20°C, dew point should be around 9.3°C
        dp = calculate_dew_point(20.0, 50.0)
        assert abs(dp - 9.3) < 0.5, f"Expected ~9.3°C, got {dp}"

    def test_100_percent_humidity(self) -> None:
        """At 100% RH, dew point equals temperature."""
        dp = calculate_dew_point(25.0, 100.0)
        assert abs(dp - 25.0) < 0.5

    def test_low_humidity(self) -> None:
        """Low humidity should give low dew point."""
        dp = calculate_dew_point(22.0, 20.0)
        assert dp < 0, f"Expected negative dew point for 20% RH at 22°C, got {dp}"

    def test_high_humidity_high_temp(self) -> None:
        """High humidity at high temp should give high dew point."""
        dp = calculate_dew_point(30.0, 80.0)
        assert dp > 20, f"Expected high dew point for 80% RH at 30°C, got {dp}"

    def test_invalid_humidity_zero(self) -> None:
        """Zero humidity should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_dew_point(20.0, 0)

    def test_invalid_humidity_over_100(self) -> None:
        """Humidity over 100% should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_dew_point(20.0, 110.0)

    def test_precision(self) -> None:
        """Dew point should be rounded to 1 decimal."""
        dp = calculate_dew_point(22.3, 45.7)
        assert dp == round(dp, 1)


class TestCondensationRisk:
    """Tests for condensation risk assessment."""

    def test_safe_conditions(self) -> None:
        """Normal indoor conditions should not be a condensation risk."""
        assert not is_condensation_risk(22.0, 45.0)

    def test_risky_conditions(self) -> None:
        """High humidity should trigger condensation risk."""
        assert is_condensation_risk(25.0, 80.0)

    def test_custom_threshold(self) -> None:
        """Custom threshold should be respected."""
        assert not is_condensation_risk(22.0, 50.0, threshold=20.0)
        assert is_condensation_risk(25.0, 70.0, threshold=10.0)
