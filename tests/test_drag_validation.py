import math

import pytest

from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
from rocket_sim.physics import force_breakdown_n


def _run_vertical_fall(dt: float) -> Simulation:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_n=0.0,
            burn_time_s=0.0,
            gravity_m_s2=8.0,
            air_density_kg_m3=2.0,
            drag_coefficient=1.0,
            reference_area_m2=1.0,
            physics_dt_s=dt,
            initial_position_m=Vector2(0.0, 100.0),
            initial_velocity_m_s=Vector2(0.0, 0.0),
        )
    )
    simulation.launch()
    for _ in range(round(1.0 / dt)):
        assert simulation.step()
    return simulation


def _vertical_fall_errors(dt: float) -> tuple[float, float]:
    simulation = _run_vertical_fall(dt)
    terminal_speed_m_s = 4.0
    expected_velocity_m_s = -terminal_speed_m_s * math.tanh(2.0)
    expected_altitude_m = 100.0 - 2.0 * math.log(math.cosh(2.0))
    return (
        abs(simulation.state.velocity_m_s.y - expected_velocity_m_s),
        abs(simulation.state.position_m.y - expected_altitude_m),
    )


def test_vertical_drag_fall_matches_independent_closed_form_reference() -> None:
    simulation = _run_vertical_fall(0.005)
    expected_velocity_m_s = -4.0 * math.tanh(2.0)
    expected_altitude_m = 100.0 - 2.0 * math.log(math.cosh(2.0))

    assert simulation.state.time_s == pytest.approx(1.0, abs=1e-12)
    assert simulation.state.velocity_m_s.y == pytest.approx(
        expected_velocity_m_s, abs=0.004
    )
    assert simulation.state.position_m.y == pytest.approx(
        expected_altitude_m, abs=0.015
    )
    assert simulation.state.phase is FlightPhase.COAST
    assert simulation.state.position_m.y > 90.0


def test_vertical_drag_fall_exhibits_measured_first_order_convergence() -> None:
    errors = [_vertical_fall_errors(dt) for dt in (0.02, 0.01, 0.005)]
    velocity_errors = [error[0] for error in errors]
    altitude_errors = [error[1] for error in errors]

    assert velocity_errors[0] > velocity_errors[1] > velocity_errors[2]
    assert altitude_errors[0] > altitude_errors[1] > altitude_errors[2]
    assert 1.8 < velocity_errors[0] / velocity_errors[1] < 2.2
    assert 1.8 < velocity_errors[1] / velocity_errors[2] < 2.2
    assert 1.8 < altitude_errors[0] / altitude_errors[1] < 2.2
    assert 1.8 < altitude_errors[1] / altitude_errors[2] < 2.2


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("air_density_kg_m3", 0.0),
        ("drag_coefficient", 0.0),
        ("reference_area_m2", 0.0),
    ],
)
def test_each_zero_aerodynamic_parameter_recovers_prompt_02_motion(
    field: str, value: float
) -> None:
    parameters = {
        "mass_kg": 2.0,
        "thrust_n": 12.0,
        "burn_time_s": 2.0,
        "launch_angle_rad": math.radians(30.0),
        "gravity_m_s2": 3.0,
        "air_density_kg_m3": 2.0,
        "drag_coefficient": 0.5,
        "reference_area_m2": 0.25,
        "physics_dt_s": 0.01,
        "initial_position_m": Vector2(0.0, 10.0),
        "initial_velocity_m_s": Vector2(1.0, 2.0),
    }
    parameters[field] = value
    simulation = Simulation(SimulationConfig(**parameters))
    simulation.launch()
    for _ in range(50):
        assert simulation.step()

    ax = 12.0 * math.cos(math.radians(30.0)) / 2.0
    ay = 12.0 * math.sin(math.radians(30.0)) / 2.0 - 3.0
    expected_vx = 1.0 + ax * 0.5
    expected_vy = 2.0 + ay * 0.5
    expected_x = 0.5 + 0.5 * ax * 0.5**2 + 0.5 * ax * 0.5 * 0.01
    expected_y = (
        10.0
        + 2.0 * 0.5
        + 0.5 * ay * 0.5**2
        + 0.5 * ay * 0.5 * 0.01
    )

    assert simulation.state.velocity_m_s.x == pytest.approx(expected_vx, abs=1e-12)
    assert simulation.state.velocity_m_s.y == pytest.approx(expected_vy, abs=1e-12)
    assert simulation.state.position_m.x == pytest.approx(expected_x, abs=1e-12)
    assert simulation.state.position_m.y == pytest.approx(expected_y, abs=1e-12)


def test_drag_directions_are_coherent_through_default_flight() -> None:
    simulation = Simulation()
    simulation.launch()
    powered_ascent = None
    coast_ascent = None
    descent = None

    for _ in range(1000):
        state = simulation.state
        if state.velocity_m_s.y > 0.0:
            if state.phase is FlightPhase.POWERED and powered_ascent is None:
                powered_ascent = state
            if state.phase is FlightPhase.COAST and coast_ascent is None:
                coast_ascent = state
        elif state.velocity_m_s.y < 0.0 and state.phase is FlightPhase.COAST:
            descent = state
            break
        if not simulation.step():
            break

    assert powered_ascent is not None
    assert coast_ascent is not None
    assert descent is not None

    powered_forces = force_breakdown_n(
        simulation.config, powered_ascent.time_s, powered_ascent.velocity_m_s
    )
    coast_forces = force_breakdown_n(
        simulation.config, coast_ascent.time_s, coast_ascent.velocity_m_s
    )
    descent_forces = force_breakdown_n(
        simulation.config, descent.time_s, descent.velocity_m_s
    )

    assert powered_forces.thrust_n.y > 0.0
    assert powered_forces.gravity_n.y < 0.0
    assert powered_forces.drag_n.y < 0.0
    assert coast_forces.thrust_n == Vector2(0.0, 0.0)
    assert coast_forces.gravity_n.y < 0.0
    assert coast_forces.drag_n.y < 0.0
    assert descent_forces.thrust_n == Vector2(0.0, 0.0)
    assert descent_forces.gravity_n.y < 0.0
    assert descent_forces.drag_n.y > 0.0
    assert {sample.mass_kg for sample in simulation.trajectory} == {1.0}


def test_active_drag_reduces_apogee_from_zero_drag_limit() -> None:
    with_drag = Simulation()
    without_drag = Simulation(SimulationConfig(air_density_kg_m3=0.0))

    for simulation in (with_drag, without_drag):
        simulation.launch()
        for _ in range(1000):
            if simulation.state.velocity_m_s.y < 0.0:
                break
            assert simulation.step()

    drag_apogee = max(sample.position_m.y for sample in with_drag.trajectory)
    vacuum_apogee = max(sample.position_m.y for sample in without_drag.trajectory)
    assert drag_apogee < vacuum_apogee
