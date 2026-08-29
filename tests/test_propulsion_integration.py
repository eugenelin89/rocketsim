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


def _curve(*samples: tuple[float, float]) -> ThrustCurve:
    return ThrustCurve(ThrustSample(time_s, thrust_n) for time_s, thrust_n in samples)


def test_default_curve_is_launch_admissible_without_ground_support_model() -> None:
    simulation = Simulation()

    simulation.launch()
    assert simulation.state.phase is FlightPhase.POWERED
    assert simulation.state.acceleration_m_s2.y == pytest.approx(2.19, abs=1e-12)
    assert simulation.step()

    assert simulation.state.time_s == 0.01
    assert simulation.state.velocity_m_s.y == pytest.approx(0.0379, abs=1e-12)
    assert simulation.state.position_m.y == pytest.approx(0.000379, abs=1e-12)
    assert simulation.state.has_lifted_off


def test_ground_admission_uses_first_interval_impulse_not_only_ignition_thrust() -> None:
    curve = _curve((0.0, 0.0), (0.01, 40.0), (0.1, 0.0))
    simulation = Simulation(
        SimulationConfig(
            thrust_curve=curve,
            air_density_kg_m3=0.0,
            physics_dt_s=0.01,
        )
    )

    assert curve.thrust_at(0.0) == 0.0
    assert curve.impulse_between_ns(0.0, 0.01) == pytest.approx(0.2)
    simulation.launch()

    assert not simulation.is_finished
    assert simulation.state.acceleration_m_s2.y == pytest.approx(-9.81)
    assert simulation.step()
    assert simulation.state.velocity_m_s.y == pytest.approx(0.1019)
    assert simulation.state.position_m.y == pytest.approx(0.001019)
    assert simulation.state.has_lifted_off


def test_zero_at_ignition_curve_delivers_positive_finite_interval_impulse_airborne() -> None:
    curve = _curve(
        (0.00, 0.0),
        (0.05, 28.0),
        (0.12, 24.0),
        (0.35, 20.0),
        (0.70, 16.0),
        (0.95, 8.0),
        (1.05, 0.0),
    )
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_curve=curve,
            launch_angle_rad=math.pi / 2.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=0.2,
            initial_position_m=Vector2(0.0, 10.0),
        )
    )

    assert curve.thrust_at(0.0) == 0.0
    assert curve.impulse_between_ns(0.0, 0.01) == pytest.approx(0.028, abs=1e-12)
    simulation.launch()
    for _ in range(6):
        assert simulation.step()

    assert curve.total_impulse_ns == pytest.approx(17.28, abs=1e-12)
    assert simulation.state.time_s == pytest.approx(1.2, abs=1e-12)
    assert simulation.state.velocity_m_s.y == pytest.approx(17.28, abs=1e-12)


def test_one_outer_step_splits_at_one_knot_and_preserves_outer_step_count() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_curve=_curve((0.0, 0.0), (0.2, 4.0), (1.0, 4.0)),
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=0.5,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    assert simulation.physics_step_count == 1
    assert simulation.state.velocity_m_s.x == pytest.approx(0.8, abs=1e-12)
    assert simulation.state.position_m.x == pytest.approx(0.28, abs=1e-12)
    assert [state.time_s for state in simulation.trajectory].count(0.2) == 1


def test_one_outer_step_splits_at_multiple_knots_in_order() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_curve=_curve(
                (0.0, 0.0),
                (0.1, 2.0),
                (0.2, 0.0),
                (0.3, 4.0),
                (1.0, 4.0),
            ),
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=0.5,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    assert simulation.physics_step_count == 1
    assert simulation.state.velocity_m_s.x == pytest.approx(1.2, abs=1e-12)
    assert simulation.state.position_m.x == pytest.approx(0.31, abs=1e-12)
    assert [state.time_s for state in simulation.trajectory] == [
        0.0,
        0.1,
        0.2,
        0.3,
        0.5,
    ]
    zero_knot = simulation.trajectory[2]
    assert zero_knot.phase is FlightPhase.POWERED
    assert zero_knot.acceleration_m_s2 == Vector2(0.0, 0.0)


def test_multiple_knots_recompute_active_drag_from_each_segment_start() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_curve=_curve(
                (0.0, 0.0), (0.1, 2.0), (0.2, 0.0), (0.4, 0.0)
            ),
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=2.0,
            drag_coefficient=1.0,
            reference_area_m2=0.5,
            physics_dt_s=0.3,
            initial_position_m=Vector2(0.0, 1.0),
            initial_velocity_m_s=Vector2(1.0, 0.0),
        )
    )
    simulation.launch()

    assert simulation.step()

    assert simulation.state.velocity_m_s.x == pytest.approx(
        1.03493743671875, abs=1e-12
    )
    assert simulation.state.position_m.x == pytest.approx(
        0.317981243671875, abs=1e-12
    )
    assert [state.time_s for state in simulation.trajectory] == [
        0.0,
        0.1,
        0.2,
        0.3,
    ]


def test_non_aligned_burn_end_delivers_exact_impulse_and_transitions_once() -> None:
    curve = ThrustCurve.constant(4.0, 0.35)
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_curve=curve,
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=0.2,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    simulation.launch()

    assert simulation.step()
    assert simulation.step()

    assert simulation.state.time_s == 0.4
    assert simulation.state.velocity_m_s.x == pytest.approx(1.4, abs=1e-12)
    assert simulation.state.position_m.x == pytest.approx(0.44, abs=1e-12)
    assert simulation.delivered_impulse_ns == pytest.approx(1.4, abs=1e-12)
    assert simulation.current_thrust_n == 0.0
    assert [state.time_s for state in simulation.trajectory].count(0.35) == 1
    transitions = [
        (before.phase, after.phase)
        for before, after in zip(
            simulation.trajectory, simulation.trajectory[1:], strict=False
        )
        if before.phase is not after.phase
    ]
    assert transitions == [(FlightPhase.POWERED, FlightPhase.COAST)]


def test_impulse_momentum_matches_independent_vector_reference() -> None:
    curve = _curve((0.0, 2.0), (0.5, 6.0), (1.5, 4.0), (2.0, 8.0))
    angle = math.radians(30.0)
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_curve=curve,
            launch_angle_rad=angle,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=0.7,
            initial_position_m=Vector2(0.0, 10.0),
            initial_velocity_m_s=Vector2(1.0, -2.0),
        )
    )
    simulation.launch()
    for _ in range(3):
        assert simulation.step()

    assert simulation.state.velocity_m_s.x == pytest.approx(
        1.0 + 5.0 * math.cos(angle), abs=1e-12
    )
    assert simulation.state.velocity_m_s.y == pytest.approx(0.5, abs=1e-12)


def test_exact_thrust_impulse_and_current_active_drag_telemetry_are_distinct() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_curve=_curve((0.0, 2.0), (0.2, 10.0)),
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

    assert simulation.state.velocity_m_s == Vector2(3.10625, 3.575)
    assert simulation.state.position_m == Vector2(1.310625, 10.3575)
    assert simulation.current_thrust_n == pytest.approx(6.0, abs=1e-12)
    speed = math.hypot(3.10625, 3.575)
    expected_drag_x = -0.125 * speed * 3.10625
    expected_drag_y = -0.125 * speed * 3.575
    assert simulation.current_forces.drag_n.x == pytest.approx(
        expected_drag_x, abs=1e-12
    )
    assert simulation.current_forces.drag_n.y == pytest.approx(
        expected_drag_y, abs=1e-12
    )
    assert simulation.state.acceleration_m_s2.x == pytest.approx(
        (6.0 + expected_drag_x) / 2.0, abs=1e-12
    )
    assert simulation.state.acceleration_m_s2.y == pytest.approx(
        (-6.0 + expected_drag_y) / 2.0, abs=1e-12
    )


def test_declining_thrust_changes_acceleration_before_burnout() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.0,
            thrust_curve=_curve((0.0, 10.0), (0.5, 5.0), (1.0, 0.0)),
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=0.25,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    simulation.launch()

    assert simulation.step()
    acceleration_at_quarter = simulation.state.acceleration_m_s2.x
    assert simulation.step()
    acceleration_at_half = simulation.state.acceleration_m_s2.x

    assert acceleration_at_quarter == pytest.approx(7.5, abs=1e-12)
    assert acceleration_at_half == pytest.approx(5.0, abs=1e-12)
    assert simulation.state.phase is FlightPhase.POWERED
    assert acceleration_at_half < acceleration_at_quarter
