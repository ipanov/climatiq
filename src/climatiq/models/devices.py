"""Device domain models."""

from __future__ import annotations

from enum import Enum, Flag

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """Types of controllable devices."""

    HVAC = "hvac"
    HUMIDIFIER = "humidifier"
    PURIFIER = "purifier"
    SWITCH = "switch"
    VACUUM = "vacuum"
    FAN = "fan"


class DeviceCapability(Flag):
    """Capabilities a device may support."""

    ON_OFF = 1
    TEMPERATURE_SETPOINT = 2
    MODE_SELECT = 4
    FAN_SPEED = 8
    SWING = 16
    HUMIDITY_SETPOINT = 32
    SPEED_PERCENTAGE = 64
    TARGET_HUMIDITY = 128

    @classmethod
    def hvac_full(cls) -> DeviceCapability:
        """Full HVAC capability set."""
        return cls.ON_OFF | cls.TEMPERATURE_SETPOINT | cls.MODE_SELECT | cls.FAN_SPEED | cls.SWING

    @classmethod
    def humidifier_full(cls) -> DeviceCapability:
        """Full humidifier capability set."""
        return cls.ON_OFF | cls.HUMIDITY_SETPOINT | cls.MODE_SELECT | cls.SPEED_PERCENTAGE

    @classmethod
    def switch_only(cls) -> DeviceCapability:
        """Simple on/off switch."""
        return cls.ON_OFF


class HVACMode(str, Enum):
    """HVAC operating modes."""

    OFF = "off"
    HEAT = "heat"
    COOL = "cool"
    AUTO = "auto"
    DRY = "dry"
    FAN_ONLY = "fan_only"


class Device(BaseModel):
    """A controllable device in the home."""

    id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Human-readable device name")
    device_type: DeviceType = Field(..., description="Type of device")
    capabilities: DeviceCapability = Field(..., description="What this device can do")
    zone_id: str = Field(..., description="Zone this device belongs to")
    provider: str = Field(default="homeassistant", description="Provider name (e.g., 'homeassistant', 'esphome')")
    min_runtime_minutes: int = Field(default=5, ge=0, description="Minimum time device must run before toggling")
    entity_id: str | None = Field(default=None, description="Provider-specific entity ID")

    model_config = {"frozen": False}
