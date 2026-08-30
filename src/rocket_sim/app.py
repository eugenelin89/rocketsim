"""Pygame application loop and input handling."""

from __future__ import annotations

import pygame

from .config import SimulationConfig
from .rendering import Renderer
from .setup import (
    AppAction,
    AppActionKind,
    adjusted_setup_config,
)
from .simulation import Simulation


WINDOW_SIZE = (1200, 720)
DISPLAY_FPS = 60


def dispatch_action(
    action: AppAction,
    simulation: Simulation,
    renderer: Renderer | None = None,
) -> bool:
    """Apply one shared keyboard/mouse command and report whether to continue."""

    if action.kind is AppActionKind.EXIT:
        return False
    if action.kind is AppActionKind.PRIMARY:
        simulation.toggle_pause()
    elif action.kind is AppActionKind.RESET_FLIGHT:
        simulation.reset()
    elif action.kind is AppActionKind.RESTORE_DEFAULTS:
        simulation.replace_ready_config(SimulationConfig())
    elif action.kind is AppActionKind.SINGLE_STEP:
        simulation.single_step_paused()
    elif action.kind is AppActionKind.TOGGLE_FORCE_VECTORS:
        if renderer is not None:
            renderer.toggle_force_vectors()
    elif action.kind is AppActionKind.TOGGLE_INSPECTOR:
        if renderer is not None:
            renderer.toggle_inspector()
    elif action.kind is AppActionKind.ADJUST_SETUP:
        if action.parameter is None:
            raise ValueError("setup action is missing its parameter")
        replacement = adjusted_setup_config(
            simulation.config,
            action.parameter,
            action.direction,
        )
        simulation.replace_ready_config(replacement)
    return True


def action_for_key(key: int) -> AppAction | None:
    """Map a supported key to the same typed actions used by mouse controls."""

    return {
        pygame.K_ESCAPE: AppAction(AppActionKind.EXIT),
        pygame.K_SPACE: AppAction(AppActionKind.PRIMARY),
        pygame.K_r: AppAction(AppActionKind.RESET_FLIGHT),
        pygame.K_RIGHT: AppAction(AppActionKind.SINGLE_STEP),
        pygame.K_f: AppAction(AppActionKind.TOGGLE_FORCE_VECTORS),
        pygame.K_i: AppAction(AppActionKind.TOGGLE_INSPECTOR),
    }.get(key)


def handle_keydown(
    key: int, simulation: Simulation, renderer: Renderer | None = None
) -> bool:
    """Apply one key command and return whether the app should continue."""

    action = action_for_key(key)
    if action is None:
        return True
    return dispatch_action(action, simulation, renderer)


def handle_mouse_button(
    button: int,
    position_px: tuple[int, int],
    simulation: Simulation,
    renderer: Renderer,
) -> bool:
    """Route one left click through the renderer's visible control geometry."""

    if button != 1:
        return True
    action = renderer.action_at(position_px, simulation)
    if action is None:
        return True
    return dispatch_action(action, simulation, renderer)


def handle_event(
    event: pygame.event.Event,
    simulation: Simulation,
    renderer: Renderer,
) -> bool:
    """Route one production Pygame event without duplicating action behavior."""

    if event.type == pygame.QUIT:
        return False
    if event.type == pygame.KEYDOWN:
        return handle_keydown(event.key, simulation, renderer)
    if event.type == pygame.MOUSEBUTTONDOWN:
        return handle_mouse_button(
            event.button, event.pos, simulation, renderer
        )
    return True


def run(max_frames: int | None = None) -> int:
    """Run the interactive app, optionally bounded for automated smoke tests."""

    if max_frames is not None and max_frames < 0:
        raise ValueError("max_frames must be non-negative or None")

    pygame.init()
    try:
        surface = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("RocketSim - sampled-thrust flight laboratory")
        clock = pygame.time.Clock()
        simulation = Simulation()
        renderer = Renderer(*WINDOW_SIZE)
        running = True
        frames = 0

        while running and (max_frames is None or frames < max_frames):
            elapsed_s = clock.tick(DISPLAY_FPS) / 1000.0
            for event in pygame.event.get():
                running = handle_event(event, simulation, renderer)
                if not running:
                    break

            simulation.advance_elapsed(elapsed_s)
            renderer.draw(surface, simulation)
            pygame.display.flip()
            frames += 1
    finally:
        pygame.quit()
    return 0
