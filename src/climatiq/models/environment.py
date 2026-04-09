"""Outdoor environment domain models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class OutdoorConditions(BaseModel):
    """Current outdoor weather conditions."""

    temperature: float = Field(..., description="Outdoor temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Outdoor relative humidity (%)")
    dew_point: float | None = Field(default=None, description="Outdoor dew point (°C)")
    cloud_cover: float | None = Field(default=None, ge=0, le=100, description="Cloud cover (%)")
    wind_speed: float | None = Field(default=None, ge=0, description="Wind speed (m/s)")
    solar_radiation: float | None = Field(default=None, ge=0, description="Solar radiation (W/m²)")
    pressure: float | None = Field(default=None, description="Atmospheric pressure (hPa)")
    timestamp: datetime = Field(default_factory=datetime.now)
    forecast_temp_24h: float | None = Field(default=None, description="Forecast temperature in 24h (°C)")


class AirQualityReading(BaseModel):
    """Outdoor air quality data."""

    aqi: int | None = Field(default=None, ge=0, description="Air Quality Index")
    pm25: float | None = Field(default=None, ge=0, description="PM2.5 concentration (µg/m³)")
    pm10: float | None = Field(default=None, ge=0, description="PM10 concentration (µg/m³)")
    timestamp: datetime = Field(default_factory=datetime.now)

    @property
    def is_good(self) -> bool:
        """Whether AQI is in the 'good' range (0-50 US EPA)."""
        return self.aqi is not None and self.aqi <= 50

    @property
    def is_unhealthy(self) -> bool:
        """Whether AQI is unhealthy (>100 US EPA)."""
        return self.aqi is not None and self.aqi > 100
