"""Tests for deadband controller."""

from datetime import timedelta

from climatiq.controllers.deadband import DeadbandConfig, DeadbandController


class TestDeadbandController:
    """Tests for DeadbandController."""

    def test_should_act_outside_deadband(self) -> None:
        controller = DeadbandController()
        assert controller.should_act("dev1", current_value=26.0, target_value=22.0, deadband=3.0)

    def test_should_not_act_inside_deadband(self) -> None:
        controller = DeadbandController()
        # Deadband is 3.0, so within 1.5 of target = no action
        assert not controller.should_act(
            "dev1", current_value=23.0, target_value=22.0, deadband=3.0
        )

    def test_should_act_beyond_deadband_edge(self) -> None:
        controller = DeadbandController()
        # Just past deadband boundary (22 + 1.5 = 23.5, test with 23.6)
        assert controller.should_act("dev1", current_value=23.6, target_value=22.0, deadband=3.0)

    def test_can_toggle_first_time(self) -> None:
        controller = DeadbandController()
        assert controller.can_toggle("dev1")

    def test_cannot_toggle_within_minimum_runtime(self) -> None:
        config = DeadbandConfig(minimum_runtime=timedelta(minutes=5))
        controller = DeadbandController(config)
        controller.record_toggle("dev1")
        assert not controller.can_toggle("dev1")

    def test_can_toggle_after_minimum_runtime(self) -> None:
        config = DeadbandConfig(minimum_runtime=timedelta(seconds=0))
        controller = DeadbandController(config)
        controller.record_toggle("dev1")
        assert controller.can_toggle("dev1")

    def test_uses_default_deadband(self) -> None:
        controller = DeadbandController(DeadbandConfig(temperature=2.0))
        # 1.0 deviation, deadband is 2.0, threshold is 1.0
        assert not controller.should_act("dev1", current_value=23.0, target_value=22.0)
