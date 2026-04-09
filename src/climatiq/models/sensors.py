"""Sensor domain models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SensorType(str, Enum):
    """Types of environmental sensors."""

    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    CO2 = "co2"
    PM25 = "pm25"
    PM10 = "pm10"
    TVOC = "tvoc"
    HCHO = "hcho"
    DEW_POINT = "dew_point"
    AQI = "aqi"
    PRESSURE = "pressure"
    LIGHT = "light"
    NOISE = "noise"

    @property
    def unit(self) -> str:
        """Standard unit for this sensor type."""
        units = {
            "temperature": "°C",
            "humidity": "%",
            "co2": "ppm",
            "pm25": "µg/m³",
            "pm10": "µg/m³",
            "tvoc": "mg/m³",
            "hcho": "mg/m³",
            "dew_point": "°C",
            "aqi": "",
            "pressure": "hPa",
            "light": "lux",
            "noise": "dB",
        }
        return units[self.value]

    @property
    def is_air_quality(self) -> bool:
        """Whether this sensor type measures air quality."""
        return self in (
            SensorType.CO2,
            SensorType.PM25,
            SensorType.PM10,
            SensorType.TVOC,
            SensorType.HCHO,
            SensorType.AQI,
        )


class SensorReading(BaseModel):
    """A single sensor measurement."""

    sensor_id: str = Field(..., description="Unique sensor identifier")
    sensor_type: SensorType = Field(..., description="Type of sensor")
    value: float = Field(..., description="Measured value")
    unit: str = Field(default="", description="Measurement unit")
    zone_id: str | None = Field(default=None, description="Zone this sensor belongs to")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the reading was taken"
    )
    is_outdoor: bool = Field(default=False, description="Whether this is an outdoor sensor")

    model_config = {"frozen": False}
