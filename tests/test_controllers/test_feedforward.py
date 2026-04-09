"""Tests for feedforward controller."""

from climatiq.controllers.feedforward import FeedforwardController
from climatiq.models.environment import OutdoorConditions
from climatiq.models.schedule import Season


class TestFeedforwardController:
    """Tests for FeedforwardController."""

    def test_no_solar_load_at_night(self) -> None:
        """Sun below horizon should give no solar load."""
        ctrl = FeedforwardController()
        load = ctrl.calculate_solar_load("z1", window_bearing_deg=180.0, sun_azimuth=0.0, sun_elevation=-10.0)
        assert load.intensity == "none"

    def test_direct_sun_facing_window(self) -> None:
        """Sun directly facing a south window should give high load."""
        ctrl = FeedforwardController()
        load = ctrl.calculate_solar_load(
            "z1",
            window_bearing_deg=180.0,
            sun_azimuth=180.0,
            sun_elevation=45.0,
        )
        assert load.intensity == "high"
        assert load.precool_adjustment == 2.0

    def test_sun_behind_window(self) -> None:
        """Sun behind a south window (north side) should give no load."""
        ctrl = FeedforwardController()
        load = ctrl.calculate_solar_load(
            "z1",
            window_bearing_deg=180.0,
            sun_azimuth=0.0,  # Sun in north
            sun_elevation=45.0,
        )
        assert load.intensity == "none"

    def test_cloudy_reduces_load(self) -> None:
        """Heavy clouds should reduce solar load."""
        ctrl = FeedforwardController()
        load = ctrl.calculate_solar_load(
            "z1",
            window_bearing_deg=180.0,
            sun_azimuth=180.0,
            sun_elevation=45.0,
            cloud_cover=90.0,
        )
        assert load.intensity in ("low", "none")

    def test_ventilation_good_conditions(self) -> None:
        """Good outdoor conditions should recommend window ventilation."""
        ctrl = FeedforwardController()
        outdoor = OutdoorConditions(temperature=20.0, humidity=50.0, dew_point=10.0)
        result = ctrl.should_ventilate(indoor_temp=25.0, outdoor=outdoor, aqi=30)
        assert result == "open_windows"

    def test_ventilation_bad_aqi(self) -> None:
        """Bad AQI should recommend AC."""
        ctrl = FeedforwardController()
        outdoor = OutdoorConditions(temperature=20.0, humidity=50.0)
        result = ctrl.should_ventilate(indoor_temp=25.0, outdoor=outdoor, aqi=150)
        assert result == "ac_preferred"

    def test_ventilation_too_cold_outside(self) -> None:
        """Too cold outside should recommend AC."""
        ctrl = FeedforwardController()
        outdoor = OutdoorConditions(temperature=5.0, humidity=60.0)
        result = ctrl.should_ventilate(indoor_temp=22.0, outdoor=outdoor, aqi=20)
        assert result == "ac_preferred"

    def test_ventilation_high_dew_point(self) -> None:
        """High outdoor dew point should recommend AC."""
        ctrl = FeedforwardController()
        outdoor = OutdoorConditions(temperature=25.0, humidity=80.0, dew_point=21.0)
        result = ctrl.should_ventilate(indoor_temp=22.0, outdoor=outdoor, aqi=40)
        # High humidity + warmer outdoor = keep_closed or ac_preferred
        assert result in ("ac_preferred", "keep_closed")
