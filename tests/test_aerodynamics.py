import math

import pytest

from rocket_sim import SimulationConfig, ThrustCurve, Vector2
from rocket_sim.physics import (
    acceleration_m_s2,
    drag_force_n,
    force_breakdown_n,
)


def _aerodynamic_config(**overrides: object) -> SimulationConfig:
    values = {
        "mass_kg": 2.0,
        "thrust_curve": ThrustCurve.constant(10.0, 2.0),
        "launch_angle_rad": 0.0,
        "gravity_m_s2": 3.0,
        "air_density_kg_m3": 2.0,
        "drag_coefficient": 0.5,
        "reference_area_m2": 0.25,
    }
    values.update(overrides)
    return SimulationConfig(**values)  # type: ignore[arg-type]


def test_drag_is_exactly_zero_at_zero_air_relative_speed() -> None:
    assert drag_force_n(
        _aerodynamic_config(), Vector2(0.0, 0.0)
    ) == Vector2(0.0, 0.0)


@pytest.mark.parametrize(
    "disabled_parameter",
    ("air_density_kg_m3", "drag_coefficient", "reference_area_m2"),
)
def test_zero_aerodynamic_parameter_disables_drag_exactly(
    disabled_parameter: str,
) -> None:
    config = _aerodynamic_config(**{disabled_parameter: 0.0})

    assert drag_force_n(config, Vector2(3.0, 4.0)) == Vector2(0.0, 0.0)


@pytest.mark.parametrize(
    ("velocity", "expected_force"),
    [
        (Vector2(4.0, 0.0), Vector2(-2.0, 0.0)),
        (Vector2(-4.0, 0.0), Vector2(2.0, 0.0)),
        (Vector2(0.0, 4.0), Vector2(0.0, -2.0)),
        (Vector2(0.0, -4.0), Vector2(0.0, 2.0)),
        (Vector2(3.0, 4.0), Vector2(-1.875, -2.5)),
        (Vector2(-3.0, 4.0), Vector2(1.875, -2.5)),
        (Vector2(3.0, -4.0), Vector2(-1.875, 2.5)),
        (Vector2(-3.0, -4.0), Vector2(1.875, 2.5)),
    ],
)
def test_drag_has_independent_expected_direction_and_components(
    velocity: Vector2, expected_force: Vector2
) -> None:
    force = drag_force_n(_aerodynamic_config(), velocity)

    assert force.x == pytest.approx(expected_force.x, abs=1e-12)
    assert force.y == pytest.approx(expected_force.y, abs=1e-12)
    assert force.x * velocity.x + force.y * velocity.y < 0.0


def test_drag_magnitude_matches_scalar_quadratic_equation() -> None:
    force = drag_force_n(_aerodynamic_config(), Vector2(3.0, 4.0))

    assert force.magnitude == pytest.approx(3.125, abs=1e-12)


def test_doubling_speed_multiplies_drag_magnitude_by_four() -> None:
    config = _aerodynamic_config()
    slower = drag_force_n(config, Vector2(3.0, 4.0))
    faster = drag_force_n(config, Vector2(6.0, 8.0))

    assert faster.magnitude == pytest.approx(4.0 * slower.magnitude, abs=1e-12)


def test_reversing_velocity_reverses_drag_force() -> None:
    config = _aerodynamic_config()
    forward = drag_force_n(config, Vector2(3.0, -4.0))
    reverse = drag_force_n(config, Vector2(-3.0, 4.0))

    assert reverse == forward * -1.0


def test_force_breakdown_and_acceleration_match_literal_oracle() -> None:
    config = _aerodynamic_config()
    velocity = Vector2(3.0, 4.0)

    forces = force_breakdown_n(config, 0.25, velocity)
    acceleration = acceleration_m_s2(config, 0.25, velocity)

    assert forces.thrust_n.x == pytest.approx(10.0, abs=1e-12)
    assert forces.thrust_n.y == pytest.approx(0.0, abs=1e-12)
    assert forces.gravity_n == Vector2(0.0, -6.0)
    assert forces.drag_n == Vector2(-1.875, -2.5)
    assert forces.net_n == Vector2(8.125, -8.5)
    assert acceleration == Vector2(4.0625, -4.25)


def test_terminal_velocity_is_force_equilibrium_with_restoring_signs() -> None:
    config = SimulationConfig(
        mass_kg=2.0,
        thrust_curve=ThrustCurve.zero(),
        gravity_m_s2=8.0,
        air_density_kg_m3=2.0,
        drag_coefficient=1.0,
        reference_area_m2=1.0,
        initial_position_m=Vector2(0.0, 100.0),
    )

    at_terminal = acceleration_m_s2(config, 1.0, Vector2(0.0, -4.0))
    below_terminal = acceleration_m_s2(config, 1.0, Vector2(0.0, -3.0))
    above_terminal = acceleration_m_s2(config, 1.0, Vector2(0.0, -5.0))

    assert at_terminal == Vector2(0.0, 0.0)
    assert below_terminal.y == pytest.approx(-3.5, abs=1e-12)
    assert above_terminal.y == pytest.approx(4.5, abs=1e-12)


def test_default_terminal_speed_is_moderate_for_educational_scenario() -> None:
    config = SimulationConfig()
    expected = math.sqrt(
        2.0
        * config.mass_kg
        * config.gravity_m_s2
        / (
            config.air_density_kg_m3
            * config.drag_coefficient
            * config.reference_area_m2
        )
    )

    assert expected == pytest.approx(46.2116, rel=1e-5)
