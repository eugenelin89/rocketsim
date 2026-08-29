import math

import pytest

from rocket_sim import Simulation, SimulationConfig, ThrustCurve, ThrustSample, Vector2


SAMPLES = ((0.0, 4.0), (0.13, 18.0), (0.37, 7.0), (0.73, 0.0))


def _production_curve() -> ThrustCurve:
    return ThrustCurve(ThrustSample(time_s, thrust_n) for time_s, thrust_n in SAMPLES)


def _literal_thrust_n(time_s: float) -> float:
    if time_s < 0.0 or time_s >= 0.73:
        return 0.0
    for (left_t, left_n), (right_t, right_n) in zip(
        SAMPLES, SAMPLES[1:], strict=False
    ):
        if left_t <= time_s < right_t:
            fraction = (time_s - left_t) / (right_t - left_t)
            return left_n + fraction * (right_n - left_n)
    raise AssertionError("literal curve interval not found")


def _independent_rk4_reference(duration_s: float) -> tuple[float, float, float, float]:
    mass_kg = 2.0
    angle_rad = 0.3
    gravity_m_s2 = 3.0
    drag_k = 0.5 * 1.2 * 0.8 * 0.15
    state = (0.0, 100.0, 2.0, 1.0)
    time_s = 0.0
    dt_s = 1.0e-5

    def derivative(
        derivative_time_s: float,
        derivative_state: tuple[float, float, float, float],
    ) -> tuple[float, float, float, float]:
        _, _, vx_m_s, vy_m_s = derivative_state
        speed_m_s = math.hypot(vx_m_s, vy_m_s)
        thrust_n = _literal_thrust_n(derivative_time_s)
        drag_x_n = -drag_k * speed_m_s * vx_m_s
        drag_y_n = -drag_k * speed_m_s * vy_m_s
        return (
            vx_m_s,
            vy_m_s,
            (thrust_n * math.cos(angle_rad) + drag_x_n) / mass_kg,
            (
                thrust_n * math.sin(angle_rad)
                - mass_kg * gravity_m_s2
                + drag_y_n
            )
            / mass_kg,
        )

    while time_s < duration_s:
        step_s = min(dt_s, duration_s - time_s)
        k1 = derivative(time_s, state)
        k2_state = tuple(
            value + 0.5 * step_s * slope
            for value, slope in zip(state, k1, strict=True)
        )
        k2 = derivative(time_s + 0.5 * step_s, k2_state)
        k3_state = tuple(
            value + 0.5 * step_s * slope
            for value, slope in zip(state, k2, strict=True)
        )
        k3 = derivative(time_s + 0.5 * step_s, k3_state)
        k4_state = tuple(
            value + step_s * slope
            for value, slope in zip(state, k3, strict=True)
        )
        k4 = derivative(time_s + step_s, k4_state)
        state = tuple(
            value
            + (step_s / 6.0)
            * (slope1 + 2.0 * slope2 + 2.0 * slope3 + slope4)
            for value, slope1, slope2, slope3, slope4 in zip(
                state, k1, k2, k3, k4, strict=True
            )
        )
        time_s += step_s
    return state


def _run_active_drag(dt_s: float, duration_s: float = 0.6) -> Simulation:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_curve=_production_curve(),
            launch_angle_rad=0.3,
            gravity_m_s2=3.0,
            air_density_kg_m3=1.2,
            drag_coefficient=0.8,
            reference_area_m2=0.15,
            physics_dt_s=dt_s,
            initial_position_m=Vector2(0.0, 100.0),
            initial_velocity_m_s=Vector2(2.0, 1.0),
        )
    )
    simulation.launch()
    for _ in range(round(duration_s / dt_s)):
        assert simulation.step()
    return simulation


def test_sampled_thrust_with_active_drag_converges_against_independent_rk4() -> None:
    reference_x, reference_y, reference_vx, reference_vy = (
        _independent_rk4_reference(0.6)
    )
    simulations = [_run_active_drag(dt_s) for dt_s in (0.02, 0.01, 0.005)]
    position_errors = [
        math.hypot(
            simulation.state.position_m.x - reference_x,
            simulation.state.position_m.y - reference_y,
        )
        for simulation in simulations
    ]
    velocity_errors = [
        math.hypot(
            simulation.state.velocity_m_s.x - reference_vx,
            simulation.state.velocity_m_s.y - reference_vy,
        )
        for simulation in simulations
    ]

    assert position_errors[0] > position_errors[1] > position_errors[2]
    assert velocity_errors[0] > velocity_errors[1] > velocity_errors[2]
    for errors in (position_errors, velocity_errors):
        assert 1.7 < errors[0] / errors[1] < 2.3
        assert 1.7 < errors[1] / errors[2] < 2.3


@pytest.mark.parametrize("dt_s", [0.02, 0.01, 0.005])
def test_propulsion_only_final_velocity_is_timestep_independent(dt_s: float) -> None:
    angle_rad = 0.3
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_curve=_production_curve(),
            launch_angle_rad=angle_rad,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=dt_s,
            initial_position_m=Vector2(0.0, 100.0),
            initial_velocity_m_s=Vector2(2.0, 1.0),
        )
    )
    simulation.launch()
    for _ in range(round(0.8 / dt_s)):
        assert simulation.step()

    independently_summed_impulse_ns = 1.43 + 3.00 + 1.26
    delta_speed_m_s = independently_summed_impulse_ns / 2.0
    assert simulation.state.velocity_m_s.x == pytest.approx(
        2.0 + delta_speed_m_s * math.cos(angle_rad), abs=1e-11
    )
    assert simulation.state.velocity_m_s.y == pytest.approx(
        1.0 + delta_speed_m_s * math.sin(angle_rad), abs=1e-11
    )
