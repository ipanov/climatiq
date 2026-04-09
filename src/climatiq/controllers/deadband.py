"""Deadband (hysteresis) controller.

Prevents short-cycling by requiring a minimum deviation from the target
before allowing state changes. This extends compressor and device lifespan
and reduces energy waste.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class DeadbandConfig:
    """Configuration for deadband control."""

    temperature: float = 1.5  # °C deadband width
    humidity: float = 5.0  # % RH deadband width
    co2: float = 100.0  # ppm deadband width
    minimum_runtime: timedelta = field(default_factory=lambda: timedelta(minutes=5))


class DeadbandController:
    """Prevents rapid state changes within a deadband zone.

    A device should not toggle state if the current value is within
    the deadband range around the target. This prevents oscillation.
    """

    def __init__(self, config: DeadbandConfig | None = None) -> None:
        self._config = config or DeadbandConfig()
        self._last_toggle: dict[str, datetime] = {}

    def should_act(
        self,
        device_id: str,
        current_value: float,
        target_value: float,
        deadband: float | None = None,
    ) -> bool:
        """Determine if a device should act based on deadband rules.

        Args:
            device_id: Device identifier for tracking last toggle time.
            current_value: Current sensor reading.
            target_value: Target value.
            deadband: Deadband width. Uses default if None.

        Returns:
            True if the device should act (value is outside deadband).
        """
        if deadband is None:
            deadband = self._config.temperature

        deviation = abs(current_value - target_value)
        return deviation > deadband / 2

    def can_toggle(self, device_id: str) -> bool:
        """Check if enough time has passed since last toggle.

        Enforces minimum runtime to prevent short-cycling.
        """
        last = self._last_toggle.get(device_id)
        if last is None:
            return True
        return datetime.now() - last >= self._config.minimum_runtime

    def record_toggle(self, device_id: str) -> None:
        """Record that a device was toggled."""
        self._last_toggle[device_id] = datetime.now()

    @property
    def config(self) -> DeadbandConfig:
        """Current deadband configuration."""
        return self._config
