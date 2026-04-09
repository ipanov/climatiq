"""Tests for sensor domain models."""

from climatiq.models.sensors import SensorReading, SensorType


class TestSensorType:
    """Tests for SensorType enum."""

    def test_units(self) -> None:
        assert SensorType.TEMPERATURE.unit == "°C"
        assert SensorType.HUMIDITY.unit == "%"
        assert SensorType.CO2.unit == "ppm"
        assert SensorType.PM25.unit == "µg/m³"

    def test_is_air_quality(self) -> None:
        assert SensorType.CO2.is_air_quality
        assert SensorType.PM25.is_air_quality
        assert SensorType.TVOC.is_air_quality
        assert not SensorType.TEMPERATURE.is_air_quality
        assert not SensorType.HUMIDITY.is_air_quality


class TestSensorReading:
    """Tests for SensorReading model."""

    def test_basic_reading(self) -> None:
        reading = SensorReading(
            sensor_id="temp_1",
            sensor_type=SensorType.TEMPERATURE,
            value=22.5,
        )
        assert reading.sensor_id == "temp_1"
        assert reading.value == 22.5
        assert reading.zone_id is None
        assert not reading.is_outdoor

    def test_outdoor_reading(self) -> None:
        reading = SensorReading(
            sensor_id="outdoor_temp",
            sensor_type=SensorType.TEMPERATURE,
            value=15.0,
            is_outdoor=True,
        )
        assert reading.is_outdoor
