import math

import pytest

from rocket_sim import Simulation, SimulationConfig, Vector2


def _powered_position_error(dt: float) -> float:
    duration = 0.5
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_n=12.0,
            burn_time_s=2.0,
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=dt,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    simulation.launch()
    for _ in range(round(duration / dt)):
        assert simulation.step()

    analytical_x = 0.5 * (12.0 / 2.0) * duration**2
    return abs(simulation.state.position_m.x - analytical_x)


def test_semi_implicit_euler_has_first_order_position_convergence() -> None:
    errors = [_powered_position_error(dt) for dt in (0.02, 0.01, 0.005)]

    assert errors[0] > errors[1] > errors[2]
    assert errors[0] / errors[1] == pytest.approx(2.0, rel=0.05)
    assert errors[1] / errors[2] == pytest.approx(2.0, rel=0.05)


def _default_landing_time_error(dt: float, analytical_time_s: float) -> float:
    simulation = Simulation(
        SimulationConfig(physics_dt_s=dt, air_density_kg_m3=0.0)
    )
    simulation.launch()
    for _ in range(2000):
        if not simulation.step():
            break
    assert simulation.is_finished
    return abs(simulation.state.time_s - analytical_time_s)


def test_interpolated_landing_time_converges_to_piecewise_analytical_root() -> None:
    powered_acceleration = 20.0 - 9.81
    burnout_altitude = 0.5 * powered_acceleration
    burnout_velocity = powered_acceleration
    coast_duration = (
        burnout_velocity
        + math.sqrt(
            burnout_velocity**2 + 2.0 * 9.81 * burnout_altitude
        )
    ) / 9.81
    analytical_landing_time_s = 1.0 + coast_duration

    errors = [
        _default_landing_time_error(dt, analytical_landing_time_s)
        for dt in (0.02, 0.01, 0.005)
    ]

    assert errors[0] > errors[1] > errors[2]
    assert errors[0] / errors[1] == pytest.approx(2.0, rel=0.05)
    assert errors[1] / errors[2] == pytest.approx(2.0, rel=0.05)
