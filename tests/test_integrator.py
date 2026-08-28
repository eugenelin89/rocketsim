import pytest

from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
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
        thrust_n=10.0,
        burn_time_s=0.75,
        launch_angle_rad=0.0,
        gravity_m_s2=0.0,
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
