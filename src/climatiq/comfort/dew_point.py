"""Dew point calculation using the Magnus formula.

The Magnus-Tetens approximation is accurate to within ±0.4°C for
temperatures between 0°C and 60°C, which covers all indoor scenarios.
"""

from __future__ import annotations

import math


def calculate_dew_point(temperature: float, humidity: float) -> float:
    """Calculate dew point using the Magnus formula.

    Formula: Td = b * gamma / (a - gamma)
    where gamma = (a * T) / (b + T) + ln(RH / 100)
    Constants: a = 17.27, b = 237.7

    Args:
        temperature: Air temperature in °C.
        humidity: Relative humidity in %.

    Returns:
        Dew point temperature in °C.

    Raises:
        ValueError: If inputs are outside valid ranges.
    """
    if humidity <= 0:
        raise ValueError("Humidity must be positive")
    if humidity > 100:
        raise ValueError("Humidity cannot exceed 100%")

    a = 17.27
    b = 237.7

    gamma = (a * temperature / (b + temperature)) + math.log(humidity / 100.0)
    dew_point = b * gamma / (a - gamma)

    return round(dew_point, 1)


def is_condensation_risk(temperature: float, humidity: float, threshold: float = 15.0) -> bool:
    """Check if dew point exceeds the condensation risk threshold.

    Args:
        temperature: Air temperature in °C.
        humidity: Relative humidity in %.
        threshold: Maximum safe dew point in °C. Default 15°C per ASHRAE guidance.

    Returns:
        True if dew point exceeds threshold (condensation/mold risk).
    """
    return calculate_dew_point(temperature, humidity) > threshold
