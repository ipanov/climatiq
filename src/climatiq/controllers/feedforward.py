"""Feedforward (predictive) controller.

Uses weather forecasts and solar geometry to anticipate climate changes
and act proactively rather than reactively. This is the key differentiator
that enables pre-cooling before solar heat gain and pre-heating before
cold weather arrives.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from climatiq.models.environment import OutdoorConditions
from climatiq.models.schedule import Season


@dataclass
class SolarLoad:
    """Estimated solar heat gain for a zone."""

    zone_id: str
    intensity: str  # "none", "low", "medium", "high"
    precool_adjustment: float = 0.0  # °C to subtract from target for pre-cooling
    preheat_adjustment: float = 0.0  # °C to add to target for pre-heating


class FeedforwardController:
    """Predictive climate control using weather and solar data.

    Implements feedforward control by:
    1. Calculating solar heat gain based on window orientation and sun position
    2. Using weather forecasts to adjust targets proactively
    3. Recommending pre-cooling or pre-heating before conditions change
    """

    def calculate_solar_load(
        self,
        zone_id: str,
        window_bearing_deg: float,
        sun_azimuth: float,
        sun_elevation: float,
        cloud_cover: float | None = None,
    ) -> SolarLoad:
        """Estimate solar heat gain for a zone.

        Args:
            zone_id: Zone identifier.
            window_bearing_deg: Window facing direction in degrees from North.
            sun_azimuth: Sun azimuth in degrees from North.
            sun_elevation: Sun elevation in degrees above horizon.
            cloud_cover: Cloud cover percentage (0-100). None = clear.

        Returns:
            SolarLoad estimate with pre-cool/heat adjustments.
        """
        # Sun below horizon
        if sun_elevation < 5:
            return SolarLoad(zone_id=zone_id, intensity="none")

        # Heavy clouds block most solar gain
        if cloud_cover is not None and cloud_cover > 85:
            return SolarLoad(zone_id=zone_id, intensity="low")

        # Calculate how directly the sun faces the window
        angle_diff = abs((sun_azimuth - window_bearing_deg + 180) % 360 - 180)
        facing = angle_diff < 45  # Direct exposure
        partial = angle_diff < 90  # Partial exposure

        # Determine intensity
        if not partial:
            intensity = "none"
        elif facing and sun_elevation > 15 and (cloud_cover is None or cloud_cover < 50):
            intensity = "high"
        elif facing and (cloud_cover is None or cloud_cover < 70):
            intensity = "medium"
        elif partial and (cloud_cover is None or cloud_cover < 50):
            intensity = "medium"
        else:
            intensity = "low"

        # Calculate adjustments
        precool = 0.0
        preheat = 0.0
        if intensity == "high":
            precool = 2.0  # Pre-cool by 2°C
        elif intensity == "medium":
            precool = 1.0  # Pre-cool by 1°C

        return SolarLoad(
            zone_id=zone_id,
            intensity=intensity,
            precool_adjustment=precool,
            preheat_adjustment=preheat,
        )

    def get_forecast_adjustment(
        self,
        forecast: list[OutdoorConditions],
        current_temp: float,
        season: Season,
    ) -> float:
        """Calculate target adjustment based on weather forecast.

        If the forecast predicts significant temperature change in the next
        few hours, pre-adjust the target to reduce the thermal shock.

        Args:
            forecast: Weather forecast for the next hours.
            current_temp: Current outdoor temperature.
            season: Current season.

        Returns:
            Target temperature adjustment in °C (positive = warmer target).
        """
        if not forecast:
            return 0.0

        # Look at the next 6 hours
        near_forecast = forecast[:min(4, len(forecast))]
        if not near_forecast:
            return 0.0

        avg_forecast_temp = sum(f.temperature for f in near_forecast) / len(near_forecast)
        delta = avg_forecast_temp - current_temp

        # If significant warming predicted in summer, pre-cool more aggressively
        if season == Season.SUMMER and delta > 5:
            return -1.0

        # If significant cooling predicted in winter, pre-heat more aggressively
        if season == Season.WINTER and delta < -5:
            return 1.0

        return 0.0

    def should_ventilate(
        self,
        indoor_temp: float,
        outdoor: OutdoorConditions,
        aqi: int | None = None,
    ) -> str:
        """Determine if natural ventilation is beneficial.

        Returns:
            "open_windows", "keep_closed", or "ac_preferred"
        """
        # Bad air quality outdoors
        if aqi is not None and aqi > 100:
            return "ac_preferred"

        # Too cold or too hot outside
        if outdoor.temperature < 10 or outdoor.temperature > 30:
            return "ac_preferred"

        # High outdoor humidity with warmer outdoor temp
        if outdoor.humidity > 75 and outdoor.temperature > indoor_temp:
            return "keep_closed"

        # High dew point outside
        if outdoor.dew_point is not None and outdoor.dew_point > 18:
            return "ac_preferred"

        # Good conditions for ventilation
        if aqi is None or aqi <= 50:
            if 15 <= outdoor.temperature <= 27:
                return "open_windows"
        elif aqi <= 75:
            if 15 <= outdoor.temperature <= 25:
                return "open_windows"

        return "keep_closed"
