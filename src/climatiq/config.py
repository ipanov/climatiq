"""Configuration models and loader for ClimatIQ.

Supports loading home configuration from YAML files, environment variables,
or programmatic construction. Uses Pydantic for validation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from climatiq.models.comfort import ComfortTarget
from climatiq.models.devices import Device
from climatiq.models.home import Home
from climatiq.models.schedule import ScheduleEntry


class HomeConfig(BaseModel):
    """Complete home configuration for ClimatIQ.

    This is the top-level configuration object that defines a home,
    its zones, devices, and comfort targets.
    """

    home: Home
    devices: list[Device] = Field(default_factory=list)
    targets: list[ComfortTarget] = Field(default_factory=list)
    schedule: list[ScheduleEntry] = Field(default_factory=list)

    def get_zone_targets(self) -> dict[str, ComfortTarget]:
        """Map zone IDs to their comfort targets."""
        return {t.zone_id: t for t in self.targets}

    def get_zone_devices(self, zone_id: str) -> list[Device]:
        """Get all devices for a zone."""
        return [d for d in self.devices if d.zone_id == zone_id]


def load_config(path: Path | str) -> HomeConfig:
    """Load home configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Validated HomeConfig instance.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        yaml.YAMLError: If the YAML is invalid.
        pydantic.ValidationError: If the config doesn't match the schema.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        data = {}

    return HomeConfig.model_validate(data)


def load_config_from_dict(data: dict[str, Any]) -> HomeConfig:
    """Load home configuration from a dictionary.

    Useful for programmatic construction or testing.
    """
    return HomeConfig.model_validate(data)
