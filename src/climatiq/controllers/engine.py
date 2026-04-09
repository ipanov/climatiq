"""Main control engine that orchestrates all controllers.

The ControlEngine is the central coordinator that:
1. Gathers sensor data via SensorProvider
2. Assesses comfort via ComfortModel
3. Determines priority via PriorityCascade
4. Calculates actions via control strategies
5. Executes actions via DeviceController
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from climatiq.comfort.score import assess_zone_comfort
from climatiq.controllers.deadband import DeadbandConfig, DeadbandController
from climatiq.controllers.feedforward import FeedforwardController
from climatiq.controllers.priority import Priority, PriorityCascade
from climatiq.controllers.schedule import ScheduleController
from climatiq.models.comfort import ComfortResult, ComfortTarget
from climatiq.models.devices import Device, HVACMode
from climatiq.models.environment import OutdoorConditions
from climatiq.models.home import Home, Zone
from climatiq.models.sensors import SensorReading
from climatiq.providers.base import DeviceController as DeviceControllerABC
from climatiq.providers.base import SensorProvider as SensorProviderABC
from climatiq.providers.base import WeatherProvider as WeatherProviderABC


@dataclass
class ControlAction:
    """A control action to be executed."""

    device_id: str
    action: str  # "set_temperature", "turn_on", "turn_off", "set_humidity", "set_mode"
    params: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    priority: Priority = Priority.COMFORT


class ControlEngine:
    """Central climate control engine.

    Coordinates all subsystems to maintain comfort, health, and safety
    across all zones in a home.
    """

    def __init__(
        self,
        home: Home,
        sensor_provider: SensorProviderABC,
        device_controller: DeviceControllerABC,
        weather_provider: WeatherProviderABC,
        schedule: ScheduleController | None = None,
        deadband: DeadbandConfig | None = None,
    ) -> None:
        self._home = home
        self._sensors = sensor_provider
        self._devices = device_controller
        self._weather = weather_provider
        self._schedule = schedule or ScheduleController()
        self._deadband = DeadbandController(deadband)
        self._priority = PriorityCascade()
        self._feedforward = FeedforwardController()

    def evaluate_zone(
        self, zone: Zone, target: ComfortTarget
    ) -> tuple[ComfortResult, list[ControlAction]]:
        """Evaluate a single zone and determine actions.

        Args:
            zone: The zone to evaluate.
            target: Comfort targets for the zone.

        Returns:
            Tuple of (comfort assessment, list of actions to take).
        """
        readings = self._sensors.get_readings(zone_id=zone.id)
        outdoor = self._weather.get_current()
        comfort = assess_zone_comfort(readings, target)

        # Check priority cascade
        priority, issues = self._priority.evaluate(readings, comfort, outdoor)

        # If safety or health issues exist, generate immediate actions
        if priority >= Priority.HEALTH:
            actions = self._generate_emergency_actions(zone, readings, priority, issues)
            return comfort, actions

        # Normal comfort control
        actions = self._generate_comfort_actions(zone, comfort, target, readings, outdoor)
        return comfort, actions

    def evaluate_all(
        self, targets: dict[str, ComfortTarget]
    ) -> dict[str, tuple[ComfortResult, list[ControlAction]]]:
        """Evaluate all zones in the home.

        Args:
            targets: Map of zone_id to ComfortTarget.

        Returns:
            Map of zone_id to (comfort_result, actions).
        """
        results: dict[str, tuple[ComfortResult, list[ControlAction]]] = {}
        for zone in self._home.zones:
            target = targets.get(zone.id)
            if target is None:
                continue
            results[zone.id] = self.evaluate_zone(zone, target)
        return results

    def execute(self, actions: list[ControlAction]) -> list[bool]:
        """Execute a list of control actions.

        Returns:
            List of success/failure for each action.
        """
        results: list[bool] = []
        for action in actions:
            if action.action == "set_temperature":
                success = self._devices.set_state(
                    action.device_id,
                    {
                        "temperature": action.params.get("temperature"),
                        "hvac_mode": action.params.get("hvac_mode"),
                    },
                )
            elif action.action == "turn_on":
                success = self._devices.set_state(action.device_id, {"state": "on"})
            elif action.action == "turn_off":
                success = self._devices.set_state(action.device_id, {"state": "off"})
            elif action.action == "set_humidity":
                success = self._devices.set_state(
                    action.device_id,
                    {"humidity": action.params.get("humidity")},
                )
            elif action.action == "set_mode":
                success = self._devices.set_state(
                    action.device_id,
                    {"mode": action.params.get("mode")},
                )
            else:
                success = False

            if success:
                self._deadband.record_toggle(action.device_id)
            results.append(success)
        return results

    def _generate_emergency_actions(
        self,
        zone: Zone,
        readings: list[SensorReading],
        priority: Priority,
        issues: list[str],
    ) -> list[ControlAction]:
        """Generate emergency actions for safety/health conditions."""
        from climatiq.models.sensors import SensorType

        actions: list[ControlAction] = []

        # Find HVAC devices in this zone
        hvac_devices = [d for d in self._get_zone_devices(zone) if d.device_type.value == "hvac"]

        for r in readings:
            if r.sensor_type == SensorType.TEMPERATURE:
                if r.value < 5:  # Frost protection
                    for dev in hvac_devices:
                        actions.append(
                            ControlAction(
                                device_id=dev.id,
                                action="set_temperature",
                                params={"temperature": 18.0, "hvac_mode": HVACMode.HEAT.value},
                                reason=f"Frost protection: {r.value}°C",
                                priority=Priority.SAFETY,
                            )
                        )
                elif r.value > 32:  # Overheat protection
                    for dev in hvac_devices:
                        actions.append(
                            ControlAction(
                                device_id=dev.id,
                                action="set_temperature",
                                params={"temperature": 26.0, "hvac_mode": HVACMode.COOL.value},
                                reason=f"Overheat protection: {r.value}°C",
                                priority=Priority.SAFETY,
                            )
                        )

        return actions

    def _generate_comfort_actions(
        self,
        zone: Zone,
        comfort: ComfortResult,
        target: ComfortTarget,
        readings: list[SensorReading],
        outdoor: OutdoorConditions,
    ) -> list[ControlAction]:
        """Generate comfort optimization actions."""

        actions: list[ControlAction] = []

        if comfort.temperature is None:
            return actions

        hvac_devices = [d for d in self._get_zone_devices(zone) if d.device_type.value == "hvac"]

        # Check deadband
        for dev in hvac_devices:
            if not self._deadband.should_act(dev.id, comfort.temperature, target.temperature_min):
                continue
            if not self._deadband.can_toggle(dev.id):
                continue

            # Determine HVAC mode based on temperature vs target
            if comfort.temperature < target.temperature_min:
                mode = HVACMode.HEAT.value
                set_temp = target.temperature_min
            elif comfort.temperature > target.temperature_max:
                mode = HVACMode.COOL.value
                set_temp = target.temperature_max
            else:
                continue  # Within range

            actions.append(
                ControlAction(
                    device_id=dev.id,
                    action="set_temperature",
                    params={"temperature": set_temp, "hvac_mode": mode},
                    reason=f"Comfort: temp {comfort.temperature}°C, target {set_temp}°C",
                    priority=Priority.COMFORT,
                )
            )

        return actions

    def _get_zone_devices(self, zone: Zone) -> list[Device]:
        """Get all devices for a zone."""
        # This would normally query a device registry
        # For now, return empty - implementation depends on device provider
        return []
