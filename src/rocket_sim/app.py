"""Pygame application loop and input handling."""

from __future__ import annotations

import pygame

from .config import SimulationConfig
from .game import GameSession, GameView
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
    game: GameSession | None = None,
) -> bool:
    """Apply one shared keyboard/mouse command and report whether to continue."""

    if action.kind is AppActionKind.EXIT:
        return False

    if game is not None:
        if simulation is not game.simulation:
            raise ValueError("dispatcher simulation must be the active game simulation")
        if action.kind is AppActionKind.OPEN_SANDBOX:
            game.open_sandbox()
        elif action.kind is AppActionKind.OPEN_MISSIONS:
            game.open_missions()
        elif action.kind is AppActionKind.SELECT_MISSION:
            assert action.mission_index is not None
            game.select_mission(action.mission_index)
        elif action.kind is AppActionKind.BEGIN_MISSION:
            game.begin_mission()
        elif action.kind is AppActionKind.BACK_TO_MODES:
            game.view = GameView.MODE_SELECT
        elif action.kind is AppActionKind.BACK_TO_MISSIONS:
            game.open_missions()
        elif action.kind is AppActionKind.RETRY_MISSION:
            game.retry()
        elif action.kind is AppActionKind.NEXT_MISSION:
            game.next_mission()
        elif action.kind is AppActionKind.RESET_MISSION_DEFAULTS:
            game.reset_mission()
        elif action.kind is AppActionKind.PRIMARY:
            game.primary()
        elif action.kind is AppActionKind.RESET_FLIGHT:
            if game.view in {GameView.SANDBOX, GameView.MISSION_FLIGHT}:
                game.simulation.reset()
                game.countdown_remaining_s = None
        elif action.kind is AppActionKind.RESTORE_DEFAULTS:
            if game.view is GameView.MISSION_FLIGHT:
                game.restore_mission_defaults()
            elif game.view is GameView.SANDBOX:
                game.simulation.replace_ready_config(SimulationConfig())
        elif action.kind is AppActionKind.SINGLE_STEP:
            if game.view in {GameView.SANDBOX, GameView.MISSION_FLIGHT}:
                game.simulation.single_step_paused()
        elif action.kind is AppActionKind.TOGGLE_FORCE_VECTORS:
            if renderer is not None:
                renderer.toggle_force_vectors()
        elif action.kind is AppActionKind.TOGGLE_INSPECTOR:
            if renderer is not None:
                renderer.toggle_inspector()
        elif action.kind is AppActionKind.ADJUST_SETUP:
            if action.parameter is None:
                raise ValueError("setup action is missing its parameter")
            if game.view is GameView.MISSION_FLIGHT:
                game.adjust_setup(action.parameter, action.direction)
            elif game.view is GameView.SANDBOX:
                replacement = adjusted_setup_config(
                    game.simulation.config,
                    action.parameter,
                    action.direction,
                )
                game.simulation.replace_ready_config(replacement)
        return True

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
    key: int,
    simulation: Simulation,
    renderer: Renderer | None = None,
    game: GameSession | None = None,
) -> bool:
    """Apply one key command and return whether the app should continue."""

    action = action_for_key(key)
    if action is None:
        return True
    return dispatch_action(action, simulation, renderer, game)


def handle_mouse_button(
    button: int,
    position_px: tuple[int, int],
    simulation: Simulation,
    renderer: Renderer,
    game: GameSession | None = None,
) -> bool:
    """Route one left click through the renderer's visible control geometry."""

    if button != 1:
        return True
    action = renderer.action_at(position_px, simulation, game)
    if action is None:
        return True
    return dispatch_action(action, simulation, renderer, game)


def handle_event(
    event: pygame.event.Event,
    simulation: Simulation,
    renderer: Renderer,
    game: GameSession | None = None,
) -> bool:
    """Route one production Pygame event without duplicating action behavior."""

    if event.type == pygame.QUIT:
        return False
    if event.type == pygame.KEYDOWN:
        return handle_keydown(event.key, simulation, renderer, game)
    if event.type == pygame.MOUSEBUTTONDOWN:
        return handle_mouse_button(
            event.button, event.pos, simulation, renderer, game
        )
    return True


def run(max_frames: int | None = None) -> int:
    """Run the interactive app, optionally bounded for automated smoke tests."""

    if max_frames is not None and max_frames < 0:
        raise ValueError("max_frames must be non-negative or None")

    pygame.init()
    try:
        surface = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("RocketSim - Sandbox and Missions")
        clock = pygame.time.Clock()
        game = GameSession()
        renderer = Renderer(*WINDOW_SIZE)
        running = True
        frames = 0

        while running and (max_frames is None or frames < max_frames):
            elapsed_s = clock.tick(DISPLAY_FPS) / 1000.0
            for event in pygame.event.get():
                running = handle_event(
                    event, game.simulation, renderer, game
                )
                if not running:
                    break

            game.advance_elapsed(elapsed_s)
            renderer.draw(surface, game.simulation, game)
            pygame.display.flip()
            frames += 1
    finally:
        pygame.quit()
    return 0
