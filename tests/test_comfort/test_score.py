"""Tests for aggregate comfort score."""

from climatiq.comfort.score import calculate_comfort_score
from climatiq.models.comfort import ComfortLevel, PMVResult


class TestComfortScore:
    """Tests for comfort score calculation."""

    def test_perfect_conditions(self) -> None:
        """Perfect conditions should give a high score."""
        pmv = PMVResult(pmv=0.0, ppd=5.0, comfort_level=ComfortLevel.COMFORTABLE)
        score = calculate_comfort_score(
            pmv_result=pmv,
            humidity=45.0,
            dew_point=10.0,
            pm25=5.0,
        )
        assert score >= 90, f"Expected score >= 90 for perfect conditions, got {score}"

    def test_poor_conditions(self) -> None:
        """Poor conditions should give a low score."""
        pmv = PMVResult(pmv=2.0, ppd=50.0, comfort_level=ComfortLevel.WARM)
        score = calculate_comfort_score(
            pmv_result=pmv,
            humidity=80.0,
            dew_point=20.0,
            pm25=50.0,
            co2=1500.0,
        )
        assert score < 50, f"Expected score < 50 for poor conditions, got {score}"

    def test_no_data_gives_moderate_score(self) -> None:
        """Missing data should give a moderate default score."""
        score = calculate_comfort_score()
        assert 60 <= score <= 80

    def test_humidity_out_of_range(self) -> None:
        """Out-of-range humidity should reduce score."""
        good_hum = calculate_comfort_score(humidity=45.0)
        low_hum = calculate_comfort_score(humidity=15.0)
        high_hum = calculate_comfort_score(humidity=80.0)
        assert good_hum > low_hum
        assert good_hum > high_hum

    def test_pm25_impact(self) -> None:
        """High PM2.5 should significantly reduce score."""
        clean = calculate_comfort_score(pm25=5.0)
        dirty = calculate_comfort_score(pm25=60.0)
        assert clean > dirty

    def test_co2_impact(self) -> None:
        """High CO2 should reduce score."""
        fresh = calculate_comfort_score(co2=400.0)
        stale = calculate_comfort_score(co2=2000.0)
        assert fresh > stale
