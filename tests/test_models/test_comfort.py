"""Tests for comfort domain models."""

from climatiq.models.comfort import ComfortLevel, ComfortResult, ComfortTarget, PMVResult


class TestComfortLevel:
    """Tests for ComfortLevel enum."""

    def test_from_pmv_comfortable(self) -> None:
        assert ComfortLevel.from_pmv(0.0) == ComfortLevel.COMFORTABLE
        assert ComfortLevel.from_pmv(0.3) == ComfortLevel.COMFORTABLE
        assert ComfortLevel.from_pmv(-0.4) == ComfortLevel.COMFORTABLE

    def test_from_pmv_slightly_warm(self) -> None:
        assert ComfortLevel.from_pmv(0.7) == ComfortLevel.SLIGHTLY_WARM
        assert ComfortLevel.from_pmv(1.0) == ComfortLevel.SLIGHTLY_WARM

    def test_from_pmv_hot(self) -> None:
        assert ComfortLevel.from_pmv(3.0) == ComfortLevel.HOT
        assert ComfortLevel.from_pmv(2.6) == ComfortLevel.HOT

    def test_from_pmv_cold(self) -> None:
        assert ComfortLevel.from_pmv(-3.0) == ComfortLevel.COLD

    def test_is_acceptable(self) -> None:
        assert ComfortLevel.COMFORTABLE.is_acceptable
        assert ComfortLevel.SLIGHTLY_COOL.is_acceptable
        assert ComfortLevel.SLIGHTLY_WARM.is_acceptable
        assert not ComfortLevel.HOT.is_acceptable
        assert not ComfortLevel.COLD.is_acceptable


class TestPMVResult:
    """Tests for PMVResult model."""

    def test_compliant(self) -> None:
        result = PMVResult(pmv=0.3, ppd=7.0, comfort_level=ComfortLevel.COMFORTABLE)
        assert result.is_compliant

    def test_non_compliant(self) -> None:
        result = PMVResult(pmv=1.2, ppd=30.0, comfort_level=ComfortLevel.SLIGHTLY_WARM)
        assert not result.is_compliant


class TestComfortTarget:
    """Tests for ComfortTarget model."""

    def test_pmv_range(self) -> None:
        target = ComfortTarget(zone_id="test", pmv_target=0.0, pmv_tolerance=0.5)
        assert target.pmv_range == (-0.5, 0.5)

    def test_custom_pmv_range(self) -> None:
        target = ComfortTarget(zone_id="test", pmv_target=0.2, pmv_tolerance=0.3)
        low, high = target.pmv_range
        assert abs(low - (-0.1)) < 0.01
        assert abs(high - 0.5) < 0.01


class TestComfortResult:
    """Tests for ComfortResult model."""

    def test_comfortable(self) -> None:
        result = ComfortResult(zone_id="test", comfort_score=95.0, issues=[])
        assert result.is_comfortable

    def test_not_comfortable_with_issues(self) -> None:
        result = ComfortResult(zone_id="test", comfort_score=95.0, issues=["Too warm"])
        assert not result.is_comfortable

    def test_not_comfortable_low_score(self) -> None:
        result = ComfortResult(zone_id="test", comfort_score=60.0, issues=[])
        assert not result.is_comfortable
