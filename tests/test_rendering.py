import os
import ast
from pathlib import Path
from unittest.mock import PropertyMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from rocket_sim import ForceBreakdown, Simulation, SimulationConfig, Vector2
from rocket_sim.app import handle_keydown, run
from rocket_sim.rendering import (
    CONTROL_ROWS,
    Renderer,
    force_vector_endpoint,
    physics_inspector_rows,
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

    for module_name in ("config.py", "physics.py", "simulation.py"):
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
        "Ft = T(cos(theta), sin(theta))",
        "Fd = -0.5 rho Cd A |v_air| v_air",
        "Fnet = Ft + Fg + Fd",
        "a = Fnet / m",
        "Still air: v_air = v_rocket",
        "rho: 1.2250 kg/m^3",
        "Cd: 0.7500",
        "Area: 0.0100 m^2",
    ):
        assert required in text

    assert "RIGHT" in CONTROL_ROWS[0]
    assert "F force vectors" in CONTROL_ROWS[1]
    assert "I Physics Inspector" in CONTROL_ROWS[1]


def test_inspector_distinguishes_no_liftoff_from_impact() -> None:
    simulation = Simulation(
        SimulationConfig(thrust_n=0.0, burn_time_s=0.0)
    )
    simulation.launch()
    rows = physics_inspector_rows(simulation, simulation.current_forces)
    text = "\n".join(rows)

    assert simulation.is_finished
    assert not simulation.state.has_lifted_off
    assert "NO LIFTOFF / terminal initial state" in text
    assert "impact state" not in text


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
