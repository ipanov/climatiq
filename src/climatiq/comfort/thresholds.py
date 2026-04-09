"""Safety, health, and comfort thresholds.

Based on ASHRAE 55-2020, ISO 7730:2005, EN 16798-1:2019, and WHO AQG 2021.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Threshold(BaseModel):
    """A threshold with target, warning, and critical levels."""

    target: float = Field(..., description="Desired target value")
    warning: float = Field(..., description="Warning level - attention needed")
    critical: float = Field(..., description="Critical level - immediate action required")


class SafetyThresholds(BaseModel):
    """Safety-critical thresholds that always override other concerns."""

    frost_temp: float = Field(
        default=5.0, description="Indoor temp below which freeze protection activates (°C)"
    )
    overheat_temp: float = Field(
        default=32.0, description="Indoor temp above which cooling is mandatory (°C)"
    )
    co2_critical: float = Field(
        default=2000.0, description="CO2 level requiring immediate ventilation (ppm)"
    )
    humidity_critical_low: float = Field(default=15.0, description="Critically low humidity (%)")
    humidity_critical_high: float = Field(default=75.0, description="Critically high humidity (%)")


class HealthThresholds(BaseModel):
    """Health-related thresholds per WHO and EN 16798-1."""

    co2: Threshold = Field(default=Threshold(target=800, warning=1000, critical=2000))
    pm25: Threshold = Field(default=Threshold(target=12, warning=35, critical=75))
    tvoc: Threshold = Field(default=Threshold(target=0.1, warning=0.3, critical=1.0))
    hcho: Threshold = Field(default=Threshold(target=0.03, warning=0.05, critical=0.1))


class ComfortThresholds(BaseModel):
    """Comfort thresholds per ASHRAE 55 / ISO 7730."""

    pmv_target: float = Field(default=0.0, description="Target PMV value")
    pmv_tolerance: float = Field(default=0.5, description="Acceptable PMV deviation")
    ppd_max: float = Field(default=10.0, description="Maximum acceptable PPD (%)")
    dew_point_max: float = Field(
        default=15.0, description="Maximum dew point to prevent condensation (°C)"
    )
    temp_min: float = Field(default=20.0, description="Minimum comfortable temperature (°C)")
    temp_max: float = Field(default=25.0, description="Maximum comfortable temperature (°C)")
    humidity_min: float = Field(default=25.0, description="Minimum comfortable humidity (%)")
    humidity_max: float = Field(default=60.0, description="Maximum comfortable humidity (%)")


class AllThresholds(BaseModel):
    """All threshold categories combined."""

    safety: SafetyThresholds = Field(default_factory=SafetyThresholds)
    health: HealthThresholds = Field(default_factory=HealthThresholds)
    comfort: ComfortThresholds = Field(default_factory=ComfortThresholds)


# Default thresholds instance
DEFAULT_THRESHOLDS = AllThresholds()
