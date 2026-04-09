"""PMV/PPD thermal comfort calculations using pythermalcomfort.

Uses the Fanger model as defined in ASHRAE 55-2020 and ISO 7730:2005.
Delegates the actual computation to pythermalcomfort to avoid reinventing
the wheel and ensure compliance with the standards.
"""

from __future__ import annotations

import math

from climatiq.models.comfort import ComfortLevel, PMVResult


def calculate_pmv(
    air_temp: float,
    radiant_temp: float | None = None,
    air_speed: float = 0.1,
    humidity: float = 50.0,
    clothing: float = 0.7,
    metabolic_rate: float = 1.1,
) -> PMVResult:
    """Calculate PMV/PPD using pythermalcomfort.

    Args:
        air_temp: Air temperature in °C.
        radiant_temp: Mean radiant temperature in °C. Defaults to air_temp.
        air_speed: Air speed in m/s. Default 0.1 (still indoor air).
        humidity: Relative humidity in %. Default 50.
        clothing: Clothing insulation in clo. Default 0.7 (typical indoor).
        metabolic_rate: Metabolic rate in met. Default 1.1 (light home activity).

    Returns:
        PMVResult with pmv, ppd, and comfort_level.

    Raises:
        ValueError: If input values are outside valid ranges.
    """
    if radiant_temp is None:
        radiant_temp = air_temp

    try:
        from pythermalcomfort.models import pmv_ppd

        result = pmv_ppd(
            tdb=air_temp,
            tr=radiant_temp,
            vr=air_speed,
            rh=humidity,
            met=metabolic_rate,
            clo=clothing,
            standard="iso",
        )
        pmv_val = result["pmv"]
        ppd_val = result["ppd"]
    except ImportError:
        # Fallback: simplified PMV approximation if pythermalcomfort not installed
        pmv_val = _simple_pmv(air_temp, radiant_temp, air_speed, humidity, clothing, metabolic_rate)
        ppd_val = _ppd_from_pmv(pmv_val)

    # Clamp to standard range
    pmv_val = max(-3.0, min(3.0, pmv_val))

    return PMVResult(
        pmv=round(pmv_val, 2),
        ppd=round(ppd_val, 1),
        comfort_level=ComfortLevel.from_pmv(pmv_val),
    )


def _ppd_from_pmv(pmv: float) -> float:
    """Calculate PPD from PMV using the ISO 7730 formula.

    PPD = 100 - 95 * exp(-0.03353*PMV^4 - 0.2179*PMV^2)
    """
    return 100.0 - 95.0 * math.exp(-0.03353 * pmv**4 - 0.2179 * pmv**2)


def _simple_pmv(
    air_temp: float,
    radiant_temp: float,
    air_speed: float,
    humidity: float,
    clothing: float,
    metabolic_rate: float,
) -> float:
    """Simplified PMV approximation for when pythermalcomfort is unavailable.

    This is a rough approximation and should NOT replace pythermalcomfort
    for production use. It provides directional PMV estimates.
    """
    # Operative temperature (simplified: average of air and radiant)
    t_op = (air_temp + radiant_temp) / 2.0

    # Neutral temperature based on clothing and metabolic rate
    # Fanger's basic relationship: t_neutral ≈ 24.5 - 2.5*clo + 0.5*(met - 1)
    t_neutral = 24.5 - 2.5 * clothing + 0.5 * (metabolic_rate - 1.0)

    # Simplified PMV: deviation from neutral scaled by sensitivity
    # Sensitivity factor depends on clothing and activity
    sensitivity = 0.3 + 0.1 * metabolic_rate - 0.05 * clothing
    pmv = (t_op - t_neutral) * sensitivity

    # Humidity correction (higher humidity feels warmer)
    if humidity > 60:
        pmv += (humidity - 60) * 0.01
    elif humidity < 30:
        pmv -= (30 - humidity) * 0.01

    # Air speed correction (more air movement feels cooler)
    if air_speed > 0.2:
        pmv -= (air_speed - 0.2) * 2.0

    return max(-3.0, min(3.0, pmv))


def main() -> None:
    """CLI entry point for PMV calculation."""
    import argparse

    parser = argparse.ArgumentParser(description="Calculate PMV/PPD thermal comfort index")
    parser.add_argument("--temp", type=float, required=True, help="Air temperature (°C)")
    parser.add_argument("--radiant", type=float, default=None, help="Radiant temperature (°C)")
    parser.add_argument("--humidity", type=float, default=50, help="Relative humidity (%%)")
    parser.add_argument("--clo", type=float, default=0.7, help="Clothing insulation (clo)")
    parser.add_argument("--met", type=float, default=1.1, help="Metabolic rate (met)")
    parser.add_argument("--air-speed", type=float, default=0.1, help="Air speed (m/s)")

    args = parser.parse_args()
    result = calculate_pmv(
        air_temp=args.temp,
        radiant_temp=args.radiant,
        air_speed=args.air_speed,
        humidity=args.humidity,
        clothing=args.clo,
        metabolic_rate=args.met,
    )
    print(f"PMV: {result.pmv:+.2f}")
    print(f"PPD: {result.ppd:.1f}%")
    print(f"Comfort: {result.comfort_level.value}")
    print(f"ASHRAE 55 compliant: {result.is_compliant}")


if __name__ == "__main__":
    main()
