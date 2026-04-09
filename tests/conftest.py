"""Shared test fixtures and configuration."""

from __future__ import annotations

import pytest

from climatiq.models.comfort import ComfortTarget
from climatiq.models.home import Home, Zone


@pytest.fixture
def sample_zone() -> Zone:
    """A basic zone for testing."""
    return Zone(
        id="living_room",
        name="Living Room",
        window_bearing_deg=180.0,
        sensor_ids=["temp_1", "hum_1"],
        device_ids=["ac_1"],
    )


@pytest.fixture
def sample_home(sample_zone: Zone) -> Home:
    """A basic home with one zone for testing."""
    return Home(
        name="Test Home",
        zones=[sample_zone],
        latitude=41.9973,
        longitude=21.4280,
        timezone="Europe/Skopje",
    )


@pytest.fixture
def sample_target() -> ComfortTarget:
    """A basic comfort target for testing."""
    return ComfortTarget(
        zone_id="living_room",
        temperature_min=20.0,
        temperature_max=25.0,
    )
