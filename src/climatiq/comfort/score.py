"""Aggregate comfort score calculation.

Combines PMV, humidity, dew point, and air quality into a single
0-100 comfort score for a zone.
"""

from __future__ import annotations

from climatiq.comfort.dew_point import calculate_dew_point
from climatiq.comfort.pmv import calculate_pmv
from climatiq.models.comfort import ComfortResult, ComfortTarget, PMVResult
from climatiq.models.sensors import SensorReading, SensorType

# Scoring weights (must sum to 1.0)
WEIGHT_PMV = 0.40
WEIGHT_HUMIDITY = 0.25
WEIGHT_DEW_POINT = 0.15
WEIGHT_AIR_QUALITY = 0.20


def calculate_comfort_score(
    pmv_result: PMVResult | None = None,
    humidity: float | None = None,
    dew_point: float | None = None,
    pm25: float | None = None,
    co2: float | None = None,
) -> float:
    """Calculate an aggregate comfort score (0-100).

    Each component is scored 0-100, then weighted:
    - PMV compliance: 40%
    - Humidity in range: 25%
    - Dew point safe: 15%
    - Air quality: 20%

    Args:
        pmv_result: PMV calculation result. None = skip (score 70).
        humidity: Relative humidity in %. None = skip (score 70).
        dew_point: Dew point in °C. None = skip (score 70).
        pm25: PM2.5 in µg/m³. None = skip (score 70).
        co2: CO2 in ppm. None = skip.

    Returns:
        Comfort score from 0 (worst) to 100 (perfect).
    """
    scores: list[tuple[float, float]] = []  # (score, weight) pairs

    # PMV score: 100 when PMV=0, degrades as |PMV| increases
    if pmv_result is not None:
        pmv_score = max(0, 100 - abs(pmv_result.pmv) * 40)
        scores.append((pmv_score, WEIGHT_PMV))
    else:
        scores.append((70.0, WEIGHT_PMV))

    # Humidity score: 100 at 45%, degrades outside 30-60%
    if humidity is not None:
        if 30 <= humidity <= 60:
            # Peak at 45%, slight penalty at edges
            hum_score = 100 - abs(humidity - 45) * 0.5
        elif humidity < 30:
            hum_score = max(0, 50 - (30 - humidity) * 3)
        else:
            hum_score = max(0, 50 - (humidity - 60) * 3)
        scores.append((hum_score, WEIGHT_HUMIDITY))
    else:
        scores.append((70.0, WEIGHT_HUMIDITY))

    # Dew point score: 100 when < 12°C, degrades above 15°C
    if dew_point is not None:
        if dew_point < 12:
            dp_score = 100.0
        elif dew_point < 15:
            dp_score = 100 - (dew_point - 12) * (100 / 3)
        else:
            dp_score = max(0, 50 - (dew_point - 15) * 10)
        scores.append((dp_score, WEIGHT_DEW_POINT))
    else:
        scores.append((70.0, WEIGHT_DEW_POINT))

    # Air quality score: based on PM2.5 and CO2
    aq_score = 70.0  # default when no data
    if pm25 is not None:
        if pm25 < 12:
            aq_score = 100 - pm25 * 1.5
        elif pm25 < 35:
            aq_score = 80 - (pm25 - 12) * 1.5
        else:
            aq_score = max(0, 40 - (pm25 - 35) * 1.0)
    if co2 is not None:
        co2_penalty = max(0, (co2 - 800) * 0.05) if co2 > 800 else 0
        aq_score = max(0, aq_score - co2_penalty)
    scores.append((aq_score, WEIGHT_AIR_QUALITY))

    # Weighted average
    total_weight = sum(w for _, w in scores)
    weighted_sum = sum(s * w for s, w in scores)
    return round(weighted_sum / total_weight, 1)


def assess_zone_comfort(
    readings: list[SensorReading],
    target: ComfortTarget,
    clothing: float = 0.7,
    metabolic_rate: float = 1.1,
) -> ComfortResult:
    """Assess comfort for a zone based on sensor readings and targets.

    Args:
        readings: Current sensor readings for the zone.
        target: Comfort target for the zone.
        clothing: Clothing insulation in clo.
        metabolic_rate: Metabolic rate in met.

    Returns:
        Comprehensive comfort assessment.
    """
    # Extract readings by type
    temp = _get_value(readings, SensorType.TEMPERATURE)
    humidity = _get_value(readings, SensorType.HUMIDITY)
    co2 = _get_value(readings, SensorType.CO2)
    pm25 = _get_value(readings, SensorType.PM25)

    # Calculate PMV
    pmv_result = None
    if temp is not None:
        pmv_result = calculate_pmv(
            air_temp=temp,
            humidity=humidity or 50.0,
            clothing=clothing,
            metabolic_rate=metabolic_rate,
        )

    # Calculate dew point
    dew_point = None
    if temp is not None and humidity is not None:
        dew_point = calculate_dew_point(temp, humidity)

    # Calculate score
    score = calculate_comfort_score(
        pmv_result=pmv_result,
        humidity=humidity,
        dew_point=dew_point,
        pm25=pm25,
        co2=co2,
    )

    # Identify issues
    issues: list[str] = []
    if temp is not None and (temp < target.temperature_min or temp > target.temperature_max):
        issues.append(
            f"Temperature {temp}°C outside target range [{target.temperature_min}, {target.temperature_max}]"
        )
    if humidity is not None and (humidity < target.humidity_min or humidity > target.humidity_max):
        issues.append(
            f"Humidity {humidity}% outside target range [{target.humidity_min}, {target.humidity_max}]"
        )
    if dew_point is not None and dew_point > target.dew_point_max:
        issues.append(f"Dew point {dew_point}°C exceeds limit {target.dew_point_max}°C")
    if pmv_result is not None and not pmv_result.is_compliant:
        issues.append(f"PMV {pmv_result.pmv:+.2f} outside ASHRAE 55 range [-0.5, +0.5]")
    if co2 is not None and co2 > 1000:
        issues.append(f"CO2 {co2:.0f} ppm exceeds 1000 ppm threshold")
    if pm25 is not None and pm25 > 12:
        issues.append(f"PM2.5 {pm25:.1f} µg/m³ exceeds WHO guideline 12 µg/m³")

    return ComfortResult(
        zone_id=target.zone_id,
        pmv_result=pmv_result,
        temperature=temp,
        humidity=humidity,
        dew_point=dew_point,
        comfort_score=score,
        issues=issues,
    )


def _get_value(readings: list[SensorReading], sensor_type: SensorType) -> float | None:
    """Extract the latest value for a sensor type from readings."""
    for r in readings:
        if r.sensor_type == sensor_type:
            return r.value
    return None


def main() -> None:
    """CLI entry point for comfort assessment."""
    import argparse

    parser = argparse.ArgumentParser(description="Calculate ClimatIQ comfort score")
    parser.add_argument("--temp", type=float, required=True, help="Temperature (°C)")
    parser.add_argument("--humidity", type=float, required=True, help="Relative humidity (%%)")
    parser.add_argument("--pm25", type=float, default=None, help="PM2.5 (µg/m³)")
    parser.add_argument("--co2", type=float, default=None, help="CO2 (ppm)")
    args = parser.parse_args()

    from climatiq.comfort.dew_point import calculate_dew_point

    dp = calculate_dew_point(args.temp, args.humidity)
    score = calculate_comfort_score(
        humidity=args.humidity,
        dew_point=dp,
        pm25=args.pm25,
        co2=args.co2,
    )
    print(f"Dew Point: {dp}°C")
    print(f"Comfort Score: {score}/100")


if __name__ == "__main__":
    main()
