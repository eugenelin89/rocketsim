import math

import pytest

from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2


def _run_steps(simulation: Simulation, count: int) -> None:
    simulation.launch()
    for _ in range(count):
        assert simulation.step()


def test_gravity_only_matches_independent_projectile_reference() -> None:
    dt = 0.01
    duration = 1.0
    config = SimulationConfig(
        thrust_n=0.0,
        burn_time_s=0.0,
        gravity_m_s2=9.81,
        air_density_kg_m3=0.0,
        physics_dt_s=dt,
        initial_position_m=Vector2(2.0, 100.0),
        initial_velocity_m_s=Vector2(3.0, 4.0),
    )
    simulation = Simulation(config)
    _run_steps(simulation, round(duration / dt))

    expected_x = 2.0 + 3.0 * duration
    expected_y = 100.0 + 4.0 * duration - 0.5 * 9.81 * duration**2
    expected_vy = 4.0 - 9.81 * duration
    expected_position_error = 0.5 * (-9.81) * duration * dt

    assert simulation.state.position_m.x == pytest.approx(expected_x, abs=1e-12)
    assert simulation.state.velocity_m_s.x == 3.0
    assert simulation.state.velocity_m_s.y == pytest.approx(expected_vy, abs=1e-12)
    assert simulation.state.position_m.y - expected_y == pytest.approx(
        expected_position_error, abs=1e-11
    )


def test_powered_motion_matches_independent_constant_acceleration_reference() -> None:
    dt = 0.01
    duration = 0.5
    mass = 2.0
    thrust = 12.0
    angle = math.radians(30.0)
    gravity = 3.0
    config = SimulationConfig(
        mass_kg=mass,
        thrust_n=thrust,
        burn_time_s=2.0,
        launch_angle_rad=angle,
        gravity_m_s2=gravity,
        air_density_kg_m3=0.0,
        physics_dt_s=dt,
        initial_position_m=Vector2(0.0, 10.0),
        initial_velocity_m_s=Vector2(1.0, 2.0),
    )
    simulation = Simulation(config)
    _run_steps(simulation, round(duration / dt))

    ax = thrust * math.cos(angle) / mass
    ay = thrust * math.sin(angle) / mass - gravity
    expected_vx = 1.0 + ax * duration
    expected_vy = 2.0 + ay * duration
    expected_x = 1.0 * duration + 0.5 * ax * duration**2
    expected_y = 10.0 + 2.0 * duration + 0.5 * ay * duration**2

    assert simulation.state.velocity_m_s.x == pytest.approx(expected_vx, abs=1e-12)
    assert simulation.state.velocity_m_s.y == pytest.approx(expected_vy, abs=1e-12)
    assert simulation.state.position_m.x - expected_x == pytest.approx(
        0.5 * ax * duration * dt, abs=1e-12
    )
    assert simulation.state.position_m.y - expected_y == pytest.approx(
        0.5 * ay * duration * dt, abs=1e-12
    )


def test_piecewise_powered_and_coast_motion_matches_closed_form_error() -> None:
    dt = 0.01
    config = SimulationConfig(physics_dt_s=dt, air_density_kg_m3=0.0)
    simulation = Simulation(config)
    _run_steps(simulation, 150)

    powered_acceleration = 20.0 - 9.81
    coast_duration = 0.5
    burnout_velocity = powered_acceleration * 1.0
    burnout_altitude = 0.5 * powered_acceleration * 1.0**2
    expected_velocity = burnout_velocity - 9.81 * coast_duration
    expected_altitude = (
        burnout_altitude
        + burnout_velocity * coast_duration
        - 0.5 * 9.81 * coast_duration**2
    )
    expected_error = 0.5 * dt * (
        powered_acceleration * 1.0 - 9.81 * coast_duration
    )

    assert expected_velocity == pytest.approx(5.285, abs=1e-12)
    assert expected_altitude == pytest.approx(8.96375, abs=1e-12)
    assert simulation.state.velocity_m_s.y == pytest.approx(expected_velocity, abs=1e-11)
    assert simulation.state.position_m.y - expected_altitude == pytest.approx(
        expected_error, abs=1e-11
    )
    assert simulation.state.phase is FlightPhase.COAST


def test_default_vertical_launch_has_negligible_horizontal_motion() -> None:
    simulation = Simulation()
    _run_steps(simulation, 150)

    assert abs(simulation.state.position_m.x) < 1e-12
    assert simulation.trajectory[50].velocity_m_s.y > 0.0
    assert simulation.state.velocity_m_s.y < simulation.trajectory[100].velocity_m_s.y


def test_zero_gravity_powered_then_coast_limit() -> None:
    config = SimulationConfig(
        mass_kg=2.0,
        thrust_n=8.0,
        burn_time_s=0.5,
        launch_angle_rad=0.0,
        gravity_m_s2=0.0,
        air_density_kg_m3=0.0,
        physics_dt_s=0.01,
        initial_position_m=Vector2(0.0, 1.0),
    )
    simulation = Simulation(config)
    _run_steps(simulation, 100)

    assert simulation.state.velocity_m_s.x == pytest.approx(2.0, abs=1e-12)
    assert simulation.state.acceleration_m_s2 == Vector2(0.0, 0.0)
    assert simulation.state.phase is FlightPhase.COAST


def test_zero_force_preserves_uniform_motion() -> None:
    config = SimulationConfig(
        thrust_n=0.0,
        burn_time_s=0.0,
        gravity_m_s2=0.0,
        air_density_kg_m3=0.0,
        physics_dt_s=0.01,
        initial_position_m=Vector2(1.0, 10.0),
        initial_velocity_m_s=Vector2(2.0, 3.0),
    )
    simulation = Simulation(config)
    _run_steps(simulation, 100)

    assert simulation.state.position_m.x == pytest.approx(3.0, abs=1e-12)
    assert simulation.state.position_m.y == pytest.approx(13.0, abs=1e-12)
    assert simulation.state.velocity_m_s == Vector2(2.0, 3.0)
