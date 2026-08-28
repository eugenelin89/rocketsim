import math

import pytest

from rocket_sim import SimulationConfig
from rocket_sim.physics import acceleration_m_s2, gravity_force_n, thrust_force_n


def test_gravity_force_has_correct_units_and_direction() -> None:
    force = gravity_force_n(2.0, 9.81)

    assert force.x == 0.0
    assert force.y == pytest.approx(-19.62, abs=1e-12)


@pytest.mark.parametrize(
    ("angle", "expected_x", "expected_y"),
    [
        (0.0, 10.0, 0.0),
        (math.pi / 2.0, 0.0, 10.0),
        (math.pi, -10.0, 0.0),
    ],
)
def test_thrust_components_at_cardinal_angles(
    angle: float, expected_x: float, expected_y: float
) -> None:
    config = SimulationConfig(
        thrust_n=10.0, launch_angle_rad=angle, gravity_m_s2=0.0
    )

    force = thrust_force_n(config, 0.0)

    assert force.x == pytest.approx(expected_x, abs=1e-12)
    assert force.y == pytest.approx(expected_y, abs=1e-12)


def test_net_acceleration_is_force_sum_divided_by_mass() -> None:
    config = SimulationConfig(
        mass_kg=2.0,
        thrust_n=10.0,
        launch_angle_rad=0.0,
        gravity_m_s2=9.81,
    )

    acceleration = acceleration_m_s2(config, 0.25)

    assert acceleration.x == pytest.approx(5.0, abs=1e-12)
    assert acceleration.y == pytest.approx(-9.81, abs=1e-12)


def test_thrust_uses_exact_half_open_burn_interval() -> None:
    burn_time_s = 1.0
    config = SimulationConfig(thrust_n=10.0, burn_time_s=burn_time_s)

    assert thrust_force_n(config, 0.0).magnitude == pytest.approx(10.0, abs=1e-12)
    assert thrust_force_n(
        config, math.nextafter(burn_time_s, 0.0)
    ).magnitude == pytest.approx(10.0, abs=1e-12)
    assert thrust_force_n(config, burn_time_s).magnitude == 0.0
    assert thrust_force_n(
        config, math.nextafter(burn_time_s, math.inf)
    ).magnitude == 0.0
    assert thrust_force_n(config, -math.ulp(0.0)).magnitude == 0.0


def test_non_finite_force_time_is_rejected() -> None:
    with pytest.raises(ValueError):
        thrust_force_n(SimulationConfig(), math.nan)
