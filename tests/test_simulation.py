import math

import pytest

from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2


def test_default_flight_lifts_off_and_returns_to_ground_once() -> None:
    simulation = Simulation()
    simulation.launch()

    assert simulation.state.phase is FlightPhase.POWERED
    assert not simulation.is_finished
    for _ in range(1000):
        if not simulation.step():
            break

    assert simulation.is_finished
    assert simulation.state.phase is FlightPhase.LANDED
    assert simulation.state.has_lifted_off
    assert simulation.state.position_m.y == 0.0
    assert simulation.state.velocity_m_s.y < 0.0
    final_state = simulation.state
    final_history = simulation.trajectory

    assert not simulation.step()
    assert simulation.state == final_state
    assert simulation.trajectory == final_history


def test_ground_crossing_is_linearly_interpolated_on_discrete_segment() -> None:
    simulation = Simulation(
        SimulationConfig(
            thrust_n=0.0,
            burn_time_s=0.0,
            gravity_m_s2=0.0,
            physics_dt_s=0.2,
            initial_position_m=Vector2(2.0, 0.1),
            initial_velocity_m_s=Vector2(4.0, -1.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    assert simulation.state.time_s == pytest.approx(0.1, abs=1e-12)
    assert simulation.state.position_m == Vector2(2.4, 0.0)
    assert simulation.state.velocity_m_s == Vector2(4.0, -1.0)
    assert simulation.is_finished


def test_accelerated_ground_crossing_interpolates_impact_velocity() -> None:
    simulation = Simulation(
        SimulationConfig(
            thrust_n=0.0,
            burn_time_s=0.0,
            gravity_m_s2=2.0,
            physics_dt_s=0.2,
            initial_position_m=Vector2(2.0, 0.1),
            initial_velocity_m_s=Vector2(4.0, -1.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    assert simulation.state.time_s == pytest.approx(1.0 / 14.0, abs=1e-12)
    assert simulation.state.position_m.x == pytest.approx(16.0 / 7.0, abs=1e-12)
    assert simulation.state.position_m.y == 0.0
    assert simulation.state.velocity_m_s.x == 4.0
    assert simulation.state.velocity_m_s.y == pytest.approx(-8.0 / 7.0, abs=1e-12)


def test_ground_configuration_that_cannot_lift_off_terminates_without_motion() -> None:
    simulation = Simulation(
        SimulationConfig(thrust_n=0.0, burn_time_s=0.0, gravity_m_s2=9.81)
    )

    simulation.launch()

    assert simulation.is_finished
    assert simulation.state.time_s == 0.0
    assert simulation.state.position_m == Vector2(0.0, 0.0)
    assert not simulation.state.has_lifted_off


def test_under_resolved_ground_launch_never_records_negative_altitude() -> None:
    simulation = Simulation(
        SimulationConfig(
            thrust_n=0.0,
            burn_time_s=0.0,
            gravity_m_s2=9.81,
            physics_dt_s=0.1,
            initial_velocity_m_s=Vector2(0.0, 0.1),
        )
    )

    simulation.launch()

    assert simulation.is_finished
    assert simulation.state.time_s == 0.0
    assert all(sample.position_m.y >= 0.0 for sample in simulation.trajectory)


def test_ground_launch_with_downward_velocity_never_penetrates_ground() -> None:
    simulation = Simulation(
        SimulationConfig(initial_velocity_m_s=Vector2(0.0, -1.0))
    )

    simulation.launch()

    assert simulation.is_finished
    assert simulation.state.time_s == 0.0
    assert all(sample.position_m.y >= 0.0 for sample in simulation.trajectory)


def test_pre_burn_impact_telemetry_keeps_thrust_and_acceleration_consistent() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_n=1.0,
            burn_time_s=1.0,
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            physics_dt_s=0.2,
            initial_position_m=Vector2(0.0, 0.1),
            initial_velocity_m_s=Vector2(0.0, -1.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    assert simulation.is_finished
    assert simulation.state.time_s < 1.0
    assert simulation.current_thrust_n == 1.0
    assert simulation.state.acceleration_m_s2 == Vector2(1.0, 0.0)


def test_reset_reproduces_state_history_and_clears_fractional_accumulator() -> None:
    simulation = Simulation()
    frame_durations = [0.016, 0.017, 0.008, 0.021, 0.013]

    simulation.launch()
    for elapsed_s in frame_durations:
        simulation.advance_elapsed(elapsed_s)
    first_state = simulation.state
    first_history = simulation.trajectory
    first_steps = simulation.physics_step_count
    assert simulation.accumulator_s > 0.0

    simulation.reset()
    assert simulation.accumulator_s == 0.0
    assert simulation.physics_step_count == 0
    assert simulation.state.phase is FlightPhase.READY
    simulation.launch()
    for elapsed_s in frame_durations:
        simulation.advance_elapsed(elapsed_s)

    assert simulation.state == first_state
    assert simulation.trajectory == first_history
    assert simulation.physics_step_count == first_steps


@pytest.mark.parametrize("elapsed_s", [-0.01, math.nan, math.inf])
def test_invalid_elapsed_time_is_rejected(elapsed_s: float) -> None:
    with pytest.raises(ValueError):
        Simulation().advance_elapsed(elapsed_s)


def test_paused_wall_time_does_not_accumulate() -> None:
    simulation = Simulation()
    simulation.launch()
    simulation.advance_elapsed(0.015)
    simulation.toggle_pause()
    state = simulation.state
    accumulator = simulation.accumulator_s

    assert simulation.advance_elapsed(1.0) == 0
    assert simulation.state == state
    assert simulation.accumulator_s == accumulator


def test_pre_launch_wall_time_is_ignored_and_pause_can_resume() -> None:
    simulation = Simulation()
    initial_state = simulation.state
    initial_history = simulation.trajectory

    assert simulation.advance_elapsed(1.0) == 0
    assert simulation.state == initial_state
    assert simulation.trajectory == initial_history
    assert simulation.accumulator_s == 0.0
    assert simulation.physics_step_count == 0

    simulation.toggle_pause()
    simulation.advance_elapsed(0.015)
    retained_accumulator = simulation.accumulator_s
    simulation.toggle_pause()
    assert simulation.is_paused
    simulation.toggle_pause()
    assert simulation.is_running
    assert not simulation.is_paused
    simulation.advance_elapsed(
        simulation.config.physics_dt_s - simulation.accumulator_s
    )

    assert simulation.physics_step_count == 2
    assert retained_accumulator == pytest.approx(0.005, abs=1e-15)
