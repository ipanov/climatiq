"""Priority cascade controller.

Implements the priority cascade: Safety > Health > Comfort > Energy.
Higher priority always overrides lower. This ensures that safety-critical
conditions (frost, overheat, dangerous CO2) are addressed before comfort
optimizations.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any

from climatiq.comfort.thresholds import AllThresholds, DEFAULT_THRESHOLDS
from climatiq.models.comfort import ComfortResult
from climatiq.models.devices import Device
from climatiq.models.environment import OutdoorConditions
from climatiq.models.sensors import SensorReading, SensorType


class Priority(IntEnum):
    """Control priority levels. Higher number = higher priority."""

    ENERGY = 1
    COMFORT = 2
    HEALTH = 3
    SAFETY = 4


class PriorityCascade:
    """Evaluates conditions and assigns priority levels.

    The cascade ensures that:
    1. Safety issues (frost, overheat, CO2 > 2000) trigger immediate action
    2. Health issues (CO2 > 1000, PM2.5 > 35) trigger health actions
    3. Comfort issues (PMV out of range) trigger comfort adjustments
    4. Energy optimizations run only when no higher priority exists
    """

    def __init__(self, thresholds: AllThresholds | None = None) -> None:
        self._thresholds = thresholds or DEFAULT_THRESHOLDS

    def evaluate(
        self,
        readings: list[SensorReading],
        comfort: ComfortResult,
        outdoor: OutdoorConditions,
    ) -> tuple[Priority, list[str]]:
        """Evaluate current conditions and return the highest priority level.

        Args:
            readings: Current sensor readings.
            comfort: Comfort assessment for the zone.
            outdoor: Outdoor conditions.

        Returns:
            Tuple of (highest priority level, list of active issues).
        """
        issues: list[str] = []
        max_priority = Priority.ENERGY

        # Check safety conditions
        safety_issues = self._check_safety(readings)
        if safety_issues:
            issues.extend(safety_issues)
            max_priority = Priority.SAFETY

        # Check health conditions (only if no safety issues)
        if max_priority < Priority.HEALTH:
            health_issues = self._check_health(readings)
            if health_issues:
                issues.extend(health_issues)
                max_priority = Priority.HEALTH

        # Check comfort conditions (only if no health/safety issues)
        if max_priority < Priority.COMFORT:
            comfort_issues = self._check_comfort(comfort)
            if comfort_issues:
                issues.extend(comfort_issues)
                max_priority = Priority.COMFORT

        return max_priority, issues

    def _check_safety(self, readings: list[SensorReading]) -> list[str]:
        """Check for safety-critical conditions."""
        issues: list[str] = []
        thresholds = self._thresholds.safety

        for r in readings:
            if r.sensor_type == SensorType.TEMPERATURE:
                if r.value < thresholds.frost_temp:
                    issues.append(f"FROST RISK: Temperature {r.value}°C below {thresholds.frost_temp}°C")
                if r.value > thresholds.overheat_temp:
                    issues.append(f"OVERHEAT: Temperature {r.value}°C above {thresholds.overheat_temp}°C")
            elif r.sensor_type == SensorType.CO2:
                if r.value > thresholds.co2_critical:
                    issues.append(f"CO2 CRITICAL: {r.value} ppm above {thresholds.co2_critical} ppm")
            elif r.sensor_type == SensorType.HUMIDITY:
                if r.value < thresholds.humidity_critical_low:
                    issues.append(f"HUMIDITY CRITICAL LOW: {r.value}%")
                if r.value > thresholds.humidity_critical_high:
                    issues.append(f"HUMIDITY CRITICAL HIGH: {r.value}%")

        return issues

    def _check_health(self, readings: list[SensorReading]) -> list[str]:
        """Check for health-related conditions."""
        issues: list[str] = []
        thresholds = self._thresholds.health

        for r in readings:
            if r.sensor_type == SensorType.CO2 and r.value > thresholds.co2.warning:
                issues.append(f"CO2 HIGH: {r.value} ppm")
            elif r.sensor_type == SensorType.PM25 and r.value > thresholds.pm25.warning:
                issues.append(f"PM2.5 HIGH: {r.value} µg/m³")
            elif r.sensor_type == SensorType.TVOC and r.value > thresholds.tvoc.warning:
                issues.append(f"TVOC HIGH: {r.value} mg/m³")
            elif r.sensor_type == SensorType.HCHO and r.value > thresholds.hcho.warning:
                issues.append(f"HCHO HIGH: {r.value} mg/m³")

        return issues

    def _check_comfort(self, comfort: ComfortResult) -> list[str]:
        """Check for comfort-related issues."""
        return comfort.issues if comfort.comfort_score < 80 else []
