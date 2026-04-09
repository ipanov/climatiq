"""Comfort domain models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ComfortLevel(str, Enum):
    """ASHRAE 7-point thermal sensation scale mapped to comfort levels."""

    COLD = "cold"              # PMV < -2.5
    COOL = "cool"              # PMV -2.5 to -1.5
    SLIGHTLY_COOL = "slightly_cool"  # PMV -1.5 to -0.5
    COMFORTABLE = "comfortable"      # PMV -0.5 to +0.5
    SLIGHTLY_WARM = "slightly_warm"  # PMV +0.5 to +1.5
    WARM = "warm"              # PMV +1.5 to +2.5
    HOT = "hot"                # PMV > +2.5

    @classmethod
    def from_pmv(cls, pmv: float) -> ComfortLevel:
        """Map PMV value to comfort level."""
        if pmv < -2.5:
            return cls.COLD
        elif pmv < -1.5:
            return cls.COOL
        elif pmv < -0.5:
            return cls.SLIGHTLY_COOL
        elif pmv < 0.5:
            return cls.COMFORTABLE
        elif pmv < 1.5:
            return cls.SLIGHTLY_WARM
        elif pmv < 2.5:
            return cls.WARM
        else:
            return cls.HOT

    @property
    def is_acceptable(self) -> bool:
        """Whether this comfort level is within ASHRAE 55 acceptable range."""
        return self in (ComfortLevel.SLIGHTLY_COOL, ComfortLevel.COMFORTABLE, ComfortLevel.SLIGHTLY_WARM)


class PMVResult(BaseModel):
    """Result of a PMV/PPD calculation."""

    pmv: float = Field(..., description="Predicted Mean Vote (-3 to +3)")
    ppd: float = Field(..., ge=0, le=100, description="Predicted Percentage of Dissatisfied (0-100%)")
    comfort_level: ComfortLevel = Field(..., description="Mapped comfort level")

    @property
    def is_compliant(self) -> bool:
        """Whether PMV is within ASHRAE 55 acceptable range (-0.5 to +0.5)."""
        return -0.5 <= self.pmv <= 0.5


class ComfortTarget(BaseModel):
    """Comfort target for a zone."""

    zone_id: str = Field(..., description="Zone this target applies to")
    temperature_min: float = Field(default=20.0, ge=10, le=35, description="Minimum acceptable temperature (°C)")
    temperature_max: float = Field(default=25.0, ge=10, le=35, description="Maximum acceptable temperature (°C)")
    humidity_min: float = Field(default=25.0, ge=0, le=100, description="Minimum acceptable humidity (%)")
    humidity_max: float = Field(default=60.0, ge=0, le=100, description="Maximum acceptable humidity (%)")
    pmv_target: float = Field(default=0.0, ge=-3, le=3, description="Target PMV value")
    pmv_tolerance: float = Field(default=0.5, ge=0, le=3, description="Acceptable PMV deviation")
    dew_point_max: float = Field(default=15.0, description="Maximum dew point (°C) to prevent condensation")

    @property
    def pmv_range(self) -> tuple[float, float]:
        """PMV target range (min, max)."""
        return (self.pmv_target - self.pmv_tolerance, self.pmv_target + self.pmv_tolerance)


class ComfortResult(BaseModel):
    """Aggregated comfort assessment for a zone."""

    zone_id: str
    pmv_result: PMVResult | None = None
    temperature: float | None = None
    humidity: float | None = None
    dew_point: float | None = None
    comfort_score: float = Field(default=0.0, ge=0, le=100, description="Aggregate comfort score (0-100)")
    issues: list[str] = Field(default_factory=list, description="Active comfort issues")

    @property
    def is_comfortable(self) -> bool:
        """Whether all comfort criteria are met."""
        return len(self.issues) == 0 and self.comfort_score >= 80
