import os
import ast
from pathlib import Path
from unittest.mock import PropertyMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from rocket_sim import (
    ForceBreakdown,
    Simulation,
    SimulationConfig,
    ThrustCurve,
    ThrustSample,
    Vector2,
)
from rocket_sim.app import handle_keydown, run
from rocket_sim.rendering import (
    CONTROL_ROWS,
    Renderer,
    force_vector_endpoint,
    physics_inspector_rows,
    thrust_timeline_geometry,
    world_to_screen,
)


def test_world_to_screen_inverts_only_vertical_axis() -> None:
    assert world_to_screen(Vector2(2.0, 3.0), (100.0, 200.0), 10.0) == (120, 170)


def test_force_vectors_share_one_scale_and_invert_only_vertical_direction() -> None:
    origin = (100, 200)
    scale = 5.0

    assert force_vector_endpoint(origin, Vector2(2.0, 0.0), scale) == (110, 200)
    assert force_vector_endpoint(origin, Vector2(0.0, 2.0), scale) == (100, 190)
    assert force_vector_endpoint(origin, Vector2(-1.0, -3.0), scale) == (95, 215)


def test_rendering_does_not_mutate_simulation_state() -> None:
    pygame.init()
    try:
        surface = pygame.Surface((1200, 720))
        simulation = Simulation()
        simulation.launch()
        simulation.step()
        simulation.advance_elapsed(0.005)
        before = (
            simulation.state,
            simulation.trajectory,
            simulation.accumulator_s,
            simulation.config,
        )
        renderer = Renderer()

        renderer.draw(surface, simulation)
        renderer.toggle_force_vectors()
        renderer.toggle_inspector()
        renderer.draw(surface, simulation)

        assert (
            simulation.state,
            simulation.trajectory,
            simulation.accumulator_s,
            simulation.config,
        ) == before
    finally:
        pygame.quit()


def test_core_modules_do_not_depend_on_pygame() -> None:
    package_root = Path(__file__).parents[1] / "src" / "rocket_sim"

    for module_name in ("config.py", "physics.py", "propulsion.py", "simulation.py"):
        tree = ast.parse((package_root / module_name).read_text())
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported_roots.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        assert "pygame" not in imported_roots


def test_renderer_uses_production_force_breakdown_without_drag_reimplementation() -> None:
    rendering_path = Path(__file__).parents[1] / "src" / "rocket_sim" / "rendering.py"
    rendering_source = rendering_path.read_text()
    assert "drag_force_n" not in rendering_source
    assert "-0.5 *" not in rendering_source

    sentinel = ForceBreakdown(
        thrust_n=Vector2(11.0, 12.0),
        gravity_n=Vector2(13.0, 14.0),
        drag_n=Vector2(15.0, 16.0),
        net_n=Vector2(17.0, 18.0),
    )
    simulation = Simulation()
    rows = physics_inspector_rows(simulation, sentinel)

    assert any("Thrust" in row and "11.000" in row and "12.000" in row for row in rows)
    assert any("Gravity" in row and "13.000" in row and "14.000" in row for row in rows)
    assert any("Drag" in row and "15.000" in row and "16.000" in row for row in rows)
    assert any("Net" in row and "17.000" in row and "18.000" in row for row in rows)

    pygame.init()
    try:
        surface = pygame.Surface((1200, 720))
        renderer = Renderer()
        with (
            patch.object(
                Simulation,
                "current_forces",
                new_callable=PropertyMock,
                return_value=sentinel,
            ) as force_property,
            patch(
                "rocket_sim.rendering.force_vector_endpoint",
                wraps=force_vector_endpoint,
            ) as endpoint_spy,
        ):
            renderer.draw(surface, simulation)
        force_property.assert_called_once_with()
        assert [call.args[1] for call in endpoint_spy.call_args_list] == [
            sentinel.thrust_n,
            sentinel.gravity_n,
            sentinel.drag_n,
            sentinel.net_n,
        ]
        assert {
            call.args[2] for call in endpoint_spy.call_args_list
        } == {renderer.force_pixels_per_newton}
    finally:
        pygame.quit()


def test_inspector_contains_required_state_parameters_forces_and_equations() -> None:
    simulation = Simulation()
    rows = physics_inspector_rows(simulation, simulation.current_forces)
    text = "\n".join(rows)

    for required in (
        "Phase:",
        "Time:",
        "Position:",
        "Velocity:",
        "Speed:",
        "Acceleration:",
        "Mass:",
        "Thrust",
        "Gravity",
        "Drag",
        "Net",
        "rho:",
        "Cd:",
        "Area:",
        "Fg = (0, -m g)",
        "Ft(t) = T(t) (cos(theta), sin(theta))",
        "Fd = -0.5 rho Cd A |v_air| v_air",
        "Fnet = Ft + Fg + Fd",
        "a = Fnet / m",
        "I = integral T(t) dt",
        "Still air: v_air = v_rocket",
        "rho: 1.2250 kg/m^3",
        "Cd: 0.7500",
        "Area: 0.0100 m^2",
        "Motor phase: READY",
        "Current thrust:",
        "Burn-time progress:",
        "Burn duration:   1.050 s",
        "Peak stored thrust:  28.000 N",
        "Average thrust:  16.743 N",
        "Delivered impulse:   0.000 N*s",
        "Total impulse:  17.580 N*s",
    ):
        assert required in text

    assert "RIGHT" in CONTROL_ROWS[0]
    assert "F force vectors" in CONTROL_ROWS[1]
    assert "I Physics Inspector" in CONTROL_ROWS[1]


def test_inspector_motor_values_use_production_curve_and_simulation_time() -> None:
    curve = ThrustCurve(
        (
            ThrustSample(0.0, 2.0),
            ThrustSample(1.0, 6.0),
            ThrustSample(2.0, 4.0),
        )
    )
    simulation = Simulation(
        SimulationConfig(
            thrust_curve=curve,
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            physics_dt_s=0.5,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    simulation.launch()
    assert simulation.step()

    text = "\n".join(
        physics_inspector_rows(simulation, simulation.current_forces)
    )

    for expected in (
        "Motor phase: ACTIVE",
        "Current thrust:   4.000 N",
        "Burn-time progress:  25.00%",
        "Burn duration:   2.000 s",
        "Peak stored thrust:   6.000 N",
        "Average thrust:   4.500 N",
        "Delivered impulse:   1.500 N*s",
        "Total impulse:   9.000 N*s",
    ):
        assert expected in text


def test_timeline_geometry_maps_exact_production_samples_and_clamped_cursor() -> None:
    curve = ThrustCurve(
        (
            ThrustSample(0.0, 2.0),
            ThrustSample(1.0, 6.0),
            ThrustSample(2.0, 4.0),
        )
    )
    graph = pygame.Rect(10, 20, 200, 100)

    active = thrust_timeline_geometry(curve, 0.5, 4.0, graph)
    coast = thrust_timeline_geometry(curve, 3.0, 0.0, graph)

    assert active.sample_points_px == ((10, 87), (110, 20), (210, 53))
    assert active.cursor_x_px == 60
    assert active.burnout_x_px == 210
    assert active.current_thrust_n == 4.0
    assert active.cursor_time_s == 0.5
    assert active.burnout_zero_point_px == (210, 120)
    assert active.terminal_sample_is_left_limit
    assert coast.cursor_x_px == 210
    assert coast.current_thrust_n == 0.0
    assert coast.cursor_time_s == 2.0


def test_timeline_distinguishes_nonzero_terminal_left_limit_from_burnout_zero() -> None:
    curve = ThrustCurve.constant(10.0, 1.0)
    geometry = thrust_timeline_geometry(
        curve, 1.0, curve.thrust_at(1.0), pygame.Rect(10, 20, 200, 100)
    )

    assert geometry.sample_points_px[-1] == (210, 20)
    assert geometry.burnout_zero_point_px == (210, 120)
    assert geometry.terminal_sample_is_left_limit
    assert geometry.current_thrust_n == 0.0


def test_renderer_timeline_receives_configured_curve_and_current_time() -> None:
    pygame.init()
    try:
        curve = ThrustCurve(
            (ThrustSample(0.0, 3.0), ThrustSample(0.3, 0.0))
        )
        simulation = Simulation(
            SimulationConfig(
                thrust_curve=curve,
                gravity_m_s2=0.0,
                initial_position_m=Vector2(0.0, 1.0),
            )
        )
        simulation.launch()
        assert simulation.step()
        surface = pygame.Surface((1200, 720))
        renderer = Renderer()

        with patch(
            "rocket_sim.rendering.thrust_timeline_geometry",
            wraps=thrust_timeline_geometry,
        ) as geometry_spy:
            renderer.draw(surface, simulation)

        geometry_spy.assert_called_once()
        assert geometry_spy.call_args.args[0] is curve
        assert geometry_spy.call_args.args[1] == simulation.state.time_s
        assert geometry_spy.call_args.args[2] == simulation.current_thrust_n
        rendering_source = (
            Path(__file__).parents[1] / "src" / "rocket_sim" / "rendering.py"
        ).read_text()
        assert "ThrustSample(" not in rendering_source
        assert "impulse_between_ns" not in rendering_source
    finally:
        pygame.quit()


def test_inspector_distinguishes_no_liftoff_from_impact() -> None:
    simulation = Simulation(
        SimulationConfig(thrust_curve=ThrustCurve.zero())
    )
    simulation.launch()
    rows = physics_inspector_rows(simulation, simulation.current_forces)
    text = "\n".join(rows)

    assert simulation.is_finished
    assert not simulation.state.has_lifted_off
    assert "NO LIFTOFF / terminal initial state" in text
    assert "impact state" not in text


def test_zero_duration_curve_has_explicit_no_burn_inspector_status() -> None:
    simulation = Simulation(SimulationConfig(thrust_curve=ThrustCurve.zero()))
    rows = physics_inspector_rows(simulation, simulation.current_forces)
    text = "\n".join(rows)

    assert "Burnout: zero-duration curve (no burn)" in text
    assert "Motor phase: READY / NO BURN" in text
    assert "Burn-time progress: N/A (zero-duration)" in text


def test_keyboard_controls_launch_pause_reset_and_exit() -> None:
    pygame.init()
    try:
        simulation = Simulation()
        renderer = Renderer()

        assert handle_keydown(pygame.K_SPACE, simulation, renderer)
        assert simulation.is_running
        assert handle_keydown(pygame.K_SPACE, simulation, renderer)
        assert simulation.is_paused

        before_steps = simulation.physics_step_count
        before_time_s = simulation.state.time_s
        assert handle_keydown(pygame.K_RIGHT, simulation, renderer)
        assert simulation.is_paused
        assert simulation.physics_step_count == before_steps + 1
        assert simulation.state.time_s == before_time_s + simulation.config.physics_dt_s

        assert renderer.show_force_vectors
        assert renderer.show_inspector
        state_before_toggles = simulation.state
        assert handle_keydown(pygame.K_f, simulation, renderer)
        assert not renderer.show_force_vectors
        assert handle_keydown(pygame.K_i, simulation, renderer)
        assert not renderer.show_inspector
        assert handle_keydown(pygame.K_f, simulation, renderer)
        assert handle_keydown(pygame.K_i, simulation, renderer)
        assert renderer.show_force_vectors
        assert renderer.show_inspector
        assert simulation.state == state_before_toggles

        assert handle_keydown(pygame.K_SPACE, simulation, renderer)
        assert simulation.is_running
        assert not simulation.is_paused
        assert handle_keydown(pygame.K_r, simulation, renderer)
        assert simulation.state.time_s == 0.0
        assert not handle_keydown(pygame.K_ESCAPE, simulation, renderer)
    finally:
        pygame.quit()


def test_bounded_dummy_driver_application_smoke() -> None:
    assert run(max_frames=2) == 0
