import math

import pytest

from rocket_sim import (
    FlightPhase,
    Simulation,
    SimulationConfig,
    ThrustCurve,
    Vector2,
)
from rocket_sim.physics import semi_implicit_euler


def test_semi_implicit_euler_uses_updated_velocity_for_position() -> None:
    position, velocity = semi_implicit_euler(
        Vector2(3.0, 0.0),
        Vector2(2.0, 0.0),
        Vector2(4.0, 0.0),
        0.5,
    )

    assert velocity.x == 4.0
    assert position.x == 5.0


def test_step_crossing_burnout_is_split_at_exact_boundary() -> None:
    config = SimulationConfig(
        mass_kg=1.0,
        thrust_curve=ThrustCurve.constant(10.0, 0.75),
        launch_angle_rad=0.0,
        gravity_m_s2=0.0,
        air_density_kg_m3=0.0,
        physics_dt_s=0.5,
        initial_position_m=Vector2(0.0, 1.0),
    )
    simulation = Simulation(config)
    simulation.launch()

    assert simulation.step()
    assert simulation.state.time_s == 0.5
    assert simulation.state.velocity_m_s.x == 5.0
    assert simulation.state.position_m.x == 2.5

    assert simulation.step()
    assert simulation.state.time_s == 1.0
    assert simulation.state.velocity_m_s.x == 7.5
    assert simulation.state.position_m.x == 6.25
    assert simulation.state.phase is FlightPhase.COAST
    assert simulation.state.acceleration_m_s2.x == 0.0
    assert sum(sample.time_s == 0.75 for sample in simulation.trajectory) == 1
    transitions = [
        (before.phase, after.phase)
        for before, after in zip(
            simulation.trajectory, simulation.trajectory[1:], strict=False
        )
        if before.phase is not after.phase
    ]
    assert transitions == [(FlightPhase.POWERED, FlightPhase.COAST)]
    assert simulation.current_thrust_n == 0.0


def test_mass_is_constant_across_powered_coast_and_landing_states() -> None:
    simulation = Simulation()
    simulation.launch()
    for _ in range(1000):
        if not simulation.step():
            break

    assert simulation.is_finished
    assert {sample.mass_kg for sample in simulation.trajectory} == {1.0}


def test_drag_step_uses_start_velocity_then_updated_velocity_for_position() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_curve=ThrustCurve.constant(10.0, 2.0),
            launch_angle_rad=0.0,
            gravity_m_s2=3.0,
            air_density_kg_m3=2.0,
            drag_coefficient=0.5,
            reference_area_m2=0.25,
            physics_dt_s=0.1,
            initial_position_m=Vector2(1.0, 10.0),
            initial_velocity_m_s=Vector2(3.0, 4.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    assert simulation.state.velocity_m_s == Vector2(3.40625, 3.575)
    assert simulation.state.position_m == Vector2(1.340625, 10.3575)

    resulting_speed = math.hypot(3.40625, 3.575)
    expected_drag_x = -0.125 * resulting_speed * 3.40625
    expected_drag_y = -0.125 * resulting_speed * 3.575
    assert simulation.current_forces.drag_n.x == pytest.approx(
        expected_drag_x, abs=1e-12
    )
    assert simulation.current_forces.drag_n.y == pytest.approx(
        expected_drag_y, abs=1e-12
    )
    assert simulation.current_forces.net_n.x == pytest.approx(
        10.0 + expected_drag_x, abs=1e-12
    )
    assert simulation.current_forces.net_n.y == pytest.approx(
        -6.0 + expected_drag_y, abs=1e-12
    )
    assert simulation.state.acceleration_m_s2.x == pytest.approx(
        (10.0 + expected_drag_x) / 2.0, abs=1e-12
    )
    assert simulation.state.acceleration_m_s2.y == pytest.approx(
        (-6.0 + expected_drag_y) / 2.0, abs=1e-12
    )


def test_drag_is_recomputed_for_coast_substep_at_exact_burnout() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_curve=ThrustCurve.constant(4.0, 0.5),
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=1.0,
            drag_coefficient=1.0,
            reference_area_m2=1.0,
            physics_dt_s=1.0,
            initial_position_m=Vector2(0.0, 1.0),
            initial_velocity_m_s=Vector2(1.0, 0.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    burnout_state = next(
        sample for sample in simulation.trajectory if sample.time_s == 0.5
    )
    assert burnout_state.phase is FlightPhase.COAST
    assert burnout_state.velocity_m_s.x == pytest.approx(2.75, abs=1e-12)
    assert burnout_state.position_m.x == pytest.approx(1.375, abs=1e-12)
    assert burnout_state.acceleration_m_s2.x == pytest.approx(-3.78125, abs=1e-12)
    assert simulation.state.time_s == 1.0
    assert simulation.state.velocity_m_s.x == pytest.approx(0.859375, abs=1e-12)
    assert simulation.state.position_m.x == pytest.approx(1.8046875, abs=1e-12)
    assert sum(sample.time_s == 0.5 for sample in simulation.trajectory) == 1
