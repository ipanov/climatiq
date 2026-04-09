"""Abstract base classes for all providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from climatiq.models.comfort import ComfortResult, ComfortTarget, PMVResult
from climatiq.models.devices import Device
from climatiq.models.environment import AirQualityReading, OutdoorConditions
from climatiq.models.sensors import SensorReading


class SensorProvider(ABC):
    """Abstract interface for reading sensor data.

    Implementations may read from Home Assistant, MQTT, REST APIs,
    direct hardware access, or any other source.
    """

    @abstractmethod
    def get_reading(self, sensor_id: str) -> SensorReading | None:
        """Get the latest reading from a sensor."""

    @abstractmethod
    def get_readings(self, zone_id: str | None = None) -> list[SensorReading]:
        """Get all latest readings, optionally filtered by zone."""

    @abstractmethod
    def get_latest(self, sensor_id: str, sensor_type: str | None = None) -> float | None:
        """Get the latest numeric value from a sensor."""


class DeviceController(ABC):
    """Abstract interface for controlling devices.

    Implementations may control via Home Assistant services, MQTT commands,
    direct API calls, or any other method.
    """

    @abstractmethod
    def set_state(self, device_id: str, state: dict[str, Any]) -> bool:
        """Set device state (on/off, temperature, mode, etc.)."""

    @abstractmethod
    def get_state(self, device_id: str) -> dict[str, Any]:
        """Get current device state."""

    @abstractmethod
    def is_available(self, device_id: str) -> bool:
        """Check if a device is online and reachable."""


class WeatherProvider(ABC):
    """Abstract interface for outdoor weather data."""

    @abstractmethod
    def get_current(self) -> OutdoorConditions:
        """Get current outdoor conditions."""

    @abstractmethod
    def get_forecast(self, hours: int = 24) -> list[OutdoorConditions]:
        """Get weather forecast for the next N hours."""


class AirQualityProvider(ABC):
    """Abstract interface for outdoor air quality data."""

    @abstractmethod
    def get_current(self) -> AirQualityReading:
        """Get current outdoor air quality."""

    @abstractmethod
    def get_nearest_station(self) -> str:
        """Get the name of the nearest monitoring station."""


class ComfortModel(ABC):
    """Abstract interface for thermal comfort calculations.

    The default implementation uses pythermalcomfort for ASHRAE 55 / ISO 7730
    PMV/PPD calculations, but this interface allows alternative models.
    """

    @abstractmethod
    def calculate_pmv(
        self,
        air_temp: float,
        radiant_temp: float | None = None,
        air_speed: float = 0.1,
        humidity: float = 50.0,
        clothing: float = 0.7,
        metabolic_rate: float = 1.1,
    ) -> PMVResult:
        """Calculate PMV/PPD for given environmental conditions."""

    @abstractmethod
    def assess_comfort(self, readings: list[SensorReading], target: ComfortTarget) -> ComfortResult:
        """Assess comfort for a zone given sensor readings and targets."""


class ControlStrategy(ABC):
    """Abstract interface for control decision-making.

    Strategies determine what actions to take based on comfort assessments,
    outdoor conditions, and device capabilities.
    """

    @abstractmethod
    def decide(
        self,
        zone_id: str,
        comfort: ComfortResult,
        outdoor: OutdoorConditions,
        devices: list[Device],
    ) -> list[dict[str, Any]]:
        """Decide what actions to take for a zone.

        Returns a list of action dicts with keys:
        - device_id: str
        - action: str (e.g., 'set_temperature', 'turn_on', 'turn_off')
        - params: dict of action-specific parameters
        """
