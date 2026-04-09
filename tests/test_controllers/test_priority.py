"""Tests for priority cascade controller."""

from climatiq.controllers.priority import Priority, PriorityCascade
from climatiq.models.comfort import ComfortResult
from climatiq.models.environment import OutdoorConditions
from climatiq.models.sensors import SensorReading, SensorType


class TestPriorityCascade:
    """Tests for PriorityCascade."""

    def test_normal_conditions_energy_priority(self) -> None:
        """Normal conditions should default to energy priority."""
        cascade = PriorityCascade()
        readings = [
            SensorReading(sensor_id="t1", sensor_type=SensorType.TEMPERATURE, value=22.0),
        ]
        comfort = ComfortResult(zone_id="test", comfort_score=95.0, issues=[])
        outdoor = OutdoorConditions(temperature=20.0, humidity=50.0)

        priority, issues = cascade.evaluate(readings, comfort, outdoor)
        assert priority == Priority.ENERGY
        assert len(issues) == 0

    def test_frost_safety_priority(self) -> None:
        """Very low temperature should trigger safety priority."""
        cascade = PriorityCascade()
        readings = [
            SensorReading(sensor_id="t1", sensor_type=SensorType.TEMPERATURE, value=3.0),
        ]
        comfort = ComfortResult(zone_id="test", comfort_score=30.0, issues=["Cold"])
        outdoor = OutdoorConditions(temperature=-5.0, humidity=80.0)

        priority, issues = cascade.evaluate(readings, comfort, outdoor)
        assert priority == Priority.SAFETY
        assert any("FROST" in i for i in issues)

    def test_overheat_safety_priority(self) -> None:
        """Very high temperature should trigger safety priority."""
        cascade = PriorityCascade()
        readings = [
            SensorReading(sensor_id="t1", sensor_type=SensorType.TEMPERATURE, value=35.0),
        ]
        comfort = ComfortResult(zone_id="test", comfort_score=20.0, issues=["Hot"])
        outdoor = OutdoorConditions(temperature=38.0, humidity=30.0)

        priority, issues = cascade.evaluate(readings, comfort, outdoor)
        assert priority == Priority.SAFETY
        assert any("OVERHEAT" in i for i in issues)

    def test_co2_health_priority(self) -> None:
        """High CO2 should trigger health priority."""
        cascade = PriorityCascade()
        readings = [
            SensorReading(sensor_id="t1", sensor_type=SensorType.TEMPERATURE, value=22.0),
            SensorReading(sensor_id="c1", sensor_type=SensorType.CO2, value=1200.0),
        ]
        comfort = ComfortResult(zone_id="test", comfort_score=70.0, issues=[])
        outdoor = OutdoorConditions(temperature=20.0, humidity=50.0)

        priority, issues = cascade.evaluate(readings, comfort, outdoor)
        assert priority == Priority.HEALTH
        assert any("CO2" in i for i in issues)

    def test_pm25_health_priority(self) -> None:
        """High PM2.5 should trigger health priority."""
        cascade = PriorityCascade()
        readings = [
            SensorReading(sensor_id="t1", sensor_type=SensorType.TEMPERATURE, value=22.0),
            SensorReading(sensor_id="p1", sensor_type=SensorType.PM25, value=50.0),
        ]
        comfort = ComfortResult(zone_id="test", comfort_score=60.0, issues=[])
        outdoor = OutdoorConditions(temperature=20.0, humidity=50.0)

        priority, issues = cascade.evaluate(readings, comfort, outdoor)
        assert priority == Priority.HEALTH

    def test_safety_overrides_health(self) -> None:
        """Safety should take precedence over health."""
        cascade = PriorityCascade()
        readings = [
            SensorReading(sensor_id="t1", sensor_type=SensorType.TEMPERATURE, value=3.0),
            SensorReading(sensor_id="c1", sensor_type=SensorType.CO2, value=1200.0),
        ]
        comfort = ComfortResult(zone_id="test", comfort_score=20.0, issues=[])
        outdoor = OutdoorConditions(temperature=-5.0, humidity=80.0)

        priority, issues = cascade.evaluate(readings, comfort, outdoor)
        assert priority == Priority.SAFETY
