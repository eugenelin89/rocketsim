import math

import pytest

from rocket_sim import (
    FlightPhase,
    Simulation,
    SimulationConfig,
    ThrustCurve,
    ThrustSample,
    Vector2,
)


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
            thrust_curve=ThrustCurve.zero(),
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
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
            thrust_curve=ThrustCurve.zero(),
            gravity_m_s2=2.0,
            air_density_kg_m3=0.0,
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
        SimulationConfig(thrust_curve=ThrustCurve.zero(), gravity_m_s2=9.81)
    )

    simulation.launch()

    assert simulation.is_finished
    assert simulation.state.time_s == 0.0
    assert simulation.state.position_m == Vector2(0.0, 0.0)
    assert not simulation.state.has_lifted_off


def test_under_resolved_ground_launch_never_records_negative_altitude() -> None:
    simulation = Simulation(
        SimulationConfig(
            thrust_curve=ThrustCurve.zero(),
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
            thrust_curve=ThrustCurve.constant(1.0, 1.0),
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
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


def test_time_varying_thrust_impact_preserves_interpolated_event_contract() -> None:
    curve = ThrustCurve(
        (ThrustSample(0.0, 2.0), ThrustSample(1.0, 10.0))
    )
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_curve=curve,
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=0.2,
            initial_position_m=Vector2(0.0, 0.1),
            initial_velocity_m_s=Vector2(0.0, -1.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    assert simulation.is_finished
    assert simulation.state.time_s == pytest.approx(0.1)
    assert simulation.state.position_m.x == pytest.approx(0.056)
    assert simulation.state.position_m.y == 0.0
    assert simulation.state.velocity_m_s.x == pytest.approx(0.28)
    assert simulation.state.velocity_m_s.y == -1.0
    assert simulation.current_thrust_n == pytest.approx(2.8)
    assert simulation.delivered_impulse_ns == pytest.approx(0.24)
    assert simulation.state.acceleration_m_s2.x == pytest.approx(2.8)
    assert simulation.state.acceleration_m_s2.y == 0.0
    assert simulation.state.velocity_m_s.x != pytest.approx(
        simulation.delivered_impulse_ns
    )


def test_drag_telemetry_uses_interpolated_impact_velocity() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_curve=ThrustCurve.constant(1.0, 1.0),
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=2.0,
            drag_coefficient=1.0,
            reference_area_m2=1.0,
            physics_dt_s=0.2,
            initial_position_m=Vector2(0.0, 0.1),
            initial_velocity_m_s=Vector2(0.0, -1.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    expected_velocity = Vector2(0.125, -0.875)
    expected_speed = math.sqrt(0.125**2 + 0.875**2)
    expected_drag = Vector2(
        -expected_speed * 0.125,
        expected_speed * 0.875,
    )
    assert simulation.state.time_s == pytest.approx(0.125, abs=1e-12)
    assert simulation.state.velocity_m_s.x == pytest.approx(
        expected_velocity.x, abs=1e-12
    )
    assert simulation.state.velocity_m_s.y == pytest.approx(
        expected_velocity.y, abs=1e-12
    )
    assert simulation.current_forces.drag_n.x == pytest.approx(
        expected_drag.x, abs=1e-12
    )
    assert simulation.current_forces.drag_n.y == pytest.approx(
        expected_drag.y, abs=1e-12
    )
    assert simulation.state.acceleration_m_s2 == Vector2(
        1.0 + expected_drag.x,
        expected_drag.y,
    )


def test_reset_reproduces_state_history_and_clears_fractional_accumulator() -> None:
    simulation = Simulation()
    frame_durations = [0.016, 0.017, 0.008, 0.021, 0.013]

    simulation.launch()
    for elapsed_s in frame_durations:
        simulation.advance_elapsed(elapsed_s)
    first_state = simulation.state
    first_history = simulation.trajectory
    first_steps = simulation.physics_step_count
    first_forces = simulation.current_forces
    first_delivered_impulse = simulation.delivered_impulse_ns
    first_config = simulation.config
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
    assert simulation.current_forces == first_forces
    assert simulation.delivered_impulse_ns == first_delivered_impulse
    assert simulation.config == first_config


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


def test_paused_single_step_uses_production_path_and_preserves_accumulator() -> None:
    paused = Simulation()
    running = Simulation()
    for simulation in (paused, running):
        simulation.launch()
        simulation.advance_elapsed(0.015)

    paused.toggle_pause()
    before_time_s = paused.state.time_s
    before_steps = paused.physics_step_count
    before_accumulator_s = paused.accumulator_s

    assert paused.single_step_paused()
    assert running.step()

    assert paused.is_paused
    assert paused.state.time_s == pytest.approx(
        before_time_s + paused.config.physics_dt_s, abs=1e-15
    )
    assert paused.physics_step_count == before_steps + 1
    assert paused.accumulator_s == before_accumulator_s
    assert paused.state == running.state
    assert paused.trajectory == running.trajectory


def test_paused_single_step_preserves_burnout_split() -> None:
    simulation = Simulation(
        SimulationConfig(
            thrust_curve=ThrustCurve.constant(20.0, 0.015),
            physics_dt_s=0.01,
            air_density_kg_m3=1.225,
        )
    )
    simulation.launch()
    assert simulation.step()
    simulation.toggle_pause()

    assert simulation.single_step_paused()

    assert simulation.is_paused
    assert simulation.physics_step_count == 2
    assert simulation.state.time_s == pytest.approx(0.02, abs=1e-15)
    assert sum(sample.time_s == 0.015 for sample in simulation.trajectory) == 1
    assert simulation.state.phase is FlightPhase.COAST


def test_paused_single_step_crosses_sample_knot_and_updates_motor_observables() -> None:
    paused = Simulation(SimulationConfig(physics_dt_s=0.04))
    running = Simulation(SimulationConfig(physics_dt_s=0.04))
    for simulation in (paused, running):
        simulation.launch()
        assert simulation.step()

    paused.advance_elapsed(0.005)
    paused.toggle_pause()
    before_impulse = paused.delivered_impulse_ns
    before_thrust = paused.current_thrust_n
    before_accumulator = paused.accumulator_s

    assert paused.single_step_paused()
    assert running.step()

    assert paused.is_paused
    assert paused.state == running.state
    assert paused.trajectory == running.trajectory
    assert paused.accumulator_s == before_accumulator
    assert [state.time_s for state in paused.trajectory].count(0.05) == 1
    assert paused.delivered_impulse_ns > before_impulse
    assert paused.current_thrust_n != before_thrust
    assert paused.current_forces == running.current_forces


def test_paused_single_step_is_inactive_when_not_paused_live_flight() -> None:
    ready = Simulation()
    assert not ready.single_step_paused()

    ready.launch()
    assert not ready.single_step_paused()

    landed = Simulation(
        SimulationConfig(thrust_curve=ThrustCurve.zero())
    )
    landed.launch()
    assert landed.is_finished
    assert not landed.single_step_paused()
