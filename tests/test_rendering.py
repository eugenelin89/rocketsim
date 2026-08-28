import os
import ast
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from rocket_sim import Simulation, Vector2
from rocket_sim.app import handle_keydown, run
from rocket_sim.rendering import Renderer, world_to_screen


def test_world_to_screen_inverts_only_vertical_axis() -> None:
    assert world_to_screen(Vector2(2.0, 3.0), (100.0, 200.0), 10.0) == (120, 170)


def test_rendering_does_not_mutate_simulation_state() -> None:
    pygame.init()
    try:
        surface = pygame.Surface((900, 700))
        simulation = Simulation()
        simulation.launch()
        simulation.step()
        before = (simulation.state, simulation.trajectory)

        Renderer().draw(surface, simulation)

        assert (simulation.state, simulation.trajectory) == before
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


def test_keyboard_controls_launch_pause_reset_and_exit() -> None:
    simulation = Simulation()

    assert handle_keydown(pygame.K_SPACE, simulation)
    assert simulation.is_running
    assert handle_keydown(pygame.K_SPACE, simulation)
    assert simulation.is_paused
    assert handle_keydown(pygame.K_SPACE, simulation)
    assert simulation.is_running
    assert not simulation.is_paused
    assert handle_keydown(pygame.K_r, simulation)
    assert simulation.state.time_s == 0.0
    assert not handle_keydown(pygame.K_ESCAPE, simulation)


def test_bounded_dummy_driver_application_smoke() -> None:
    assert run(max_frames=2) == 0
