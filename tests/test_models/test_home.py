"""Tests for Home and Zone domain models."""

import pytest
from pydantic import ValidationError

from climatiq.models.home import Home, WindowOrientation, Zone


class TestWindowOrientation:
    """Tests for WindowOrientation enum."""

    def test_degrees_north(self) -> None:
        assert WindowOrientation.NORTH.degrees == 0.0

    def test_degrees_east(self) -> None:
        assert WindowOrientation.EAST.degrees == 90.0

    def test_degrees_south(self) -> None:
        assert WindowOrientation.SOUTH.degrees == 180.0

    def test_degrees_west(self) -> None:
        assert WindowOrientation.WEST.degrees == 270.0

    def test_from_degrees_exact(self) -> None:
        assert WindowOrientation.from_degrees(0) == WindowOrientation.NORTH
        assert WindowOrientation.from_degrees(90) == WindowOrientation.EAST
        assert WindowOrientation.from_degrees(180) == WindowOrientation.SOUTH
        assert WindowOrientation.from_degrees(270) == WindowOrientation.WEST

    def test_from_degrees_closest(self) -> None:
        assert WindowOrientation.from_degrees(10) == WindowOrientation.NORTH
        assert WindowOrientation.from_degrees(80) == WindowOrientation.EAST
        assert WindowOrientation.from_degrees(350) == WindowOrientation.NORTH

    def test_from_degrees_boundary(self) -> None:
        assert WindowOrientation.from_degrees(360) == WindowOrientation.NORTH
        assert WindowOrientation.from_degrees(45) == WindowOrientation.NORTHEAST


class TestZone:
    """Tests for Zone model."""

    def test_basic_zone(self) -> None:
        zone = Zone(id="test", name="Test Zone")
        assert zone.id == "test"
        assert zone.name == "Test Zone"
        assert zone.window_bearing_deg is None
        assert not zone.has_window

    def test_zone_with_window(self) -> None:
        zone = Zone(id="test", name="Test Zone", window_bearing_deg=180.0)
        assert zone.has_window
        assert zone.window_orientation == WindowOrientation.SOUTH

    def test_zone_invalid_bearing(self) -> None:
        with pytest.raises(ValidationError):
            Zone(id="test", name="Test", window_bearing_deg=400.0)

    def test_zone_negative_bearing(self) -> None:
        with pytest.raises(ValidationError):
            Zone(id="test", name="Test", window_bearing_deg=-10.0)


class TestHome:
    """Tests for Home model."""

    def test_basic_home(self, sample_zone: Zone) -> None:
        home = Home(name="Test", zones=[sample_zone], latitude=41.0, longitude=21.0)
        assert home.name == "Test"
        assert len(home.zones) == 1

    def test_get_zone(self, sample_home: Home) -> None:
        zone = sample_home.get_zone("living_room")
        assert zone is not None
        assert zone.name == "Living Room"

    def test_get_zone_not_found(self, sample_home: Home) -> None:
        zone = sample_home.get_zone("nonexistent")
        assert zone is None

    def test_zone_ids(self, sample_home: Home) -> None:
        assert sample_home.zone_ids == ["living_room"]

    def test_home_invalid_latitude(self) -> None:
        with pytest.raises(ValidationError):
            Home(name="Bad", latitude=100.0, longitude=0.0)

    def test_home_multiple_zones(self) -> None:
        zones = [
            Zone(id="z1", name="Zone 1"),
            Zone(id="z2", name="Zone 2"),
            Zone(id="z3", name="Zone 3"),
        ]
        home = Home(name="Big", zones=zones, latitude=0.0, longitude=0.0)
        assert len(home.zones) == 3
        assert home.zone_ids == ["z1", "z2", "z3"]
