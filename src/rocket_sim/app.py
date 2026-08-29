"""Pygame application loop and input handling."""

from __future__ import annotations

import pygame

from .rendering import Renderer
from .simulation import Simulation


WINDOW_SIZE = (1200, 720)
DISPLAY_FPS = 60


def handle_keydown(
    key: int, simulation: Simulation, renderer: Renderer | None = None
) -> bool:
    """Apply one key command and return whether the app should continue."""

    if key == pygame.K_ESCAPE:
        return False
    if key == pygame.K_SPACE:
        simulation.toggle_pause()
    elif key == pygame.K_r:
        simulation.reset()
    elif key == pygame.K_RIGHT:
        simulation.single_step_paused()
    elif key == pygame.K_f and renderer is not None:
        renderer.toggle_force_vectors()
    elif key == pygame.K_i and renderer is not None:
        renderer.toggle_inspector()
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
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = handle_keydown(event.key, simulation, renderer)

            simulation.advance_elapsed(elapsed_s)
            renderer.draw(surface, simulation)
            pygame.display.flip()
            frames += 1
    finally:
        pygame.quit()
    return 0
