"""Pygame presentation for RocketSim world state."""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from .config import Vector2
from .simulation import FlightPhase, Simulation


def world_to_screen(
    position_m: Vector2,
    origin_px: tuple[float, float],
    pixels_per_metre: float,
) -> tuple[int, int]:
    """Map +y-up world metres to +y-down screen pixels."""

    return (
        round(origin_px[0] + position_m.x * pixels_per_metre),
        round(origin_px[1] - position_m.y * pixels_per_metre),
    )


@dataclass(slots=True)
class Renderer:
    width_px: int = 900
    height_px: int = 700
    pixels_per_metre: float = 20.0
    ground_y_px: int = 620
    _font: pygame.font.Font = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._font = pygame.font.Font(None, 25)

    @property
    def origin_px(self) -> tuple[float, float]:
        return (self.width_px / 2.0, float(self.ground_y_px))

    def draw(self, surface: pygame.Surface, simulation: Simulation) -> None:
        surface.fill((12, 20, 36))
        pygame.draw.rect(
            surface,
            (52, 83, 55),
            pygame.Rect(0, self.ground_y_px, self.width_px, self.height_px),
        )
        pygame.draw.line(
            surface,
            (142, 174, 125),
            (0, self.ground_y_px),
            (self.width_px, self.ground_y_px),
            2,
        )

        points = [
            world_to_screen(sample.position_m, self.origin_px, self.pixels_per_metre)
            for sample in simulation.trajectory
        ]
        if len(points) >= 2:
            pygame.draw.lines(surface, (96, 184, 255), False, points, 2)

        rocket_x, rocket_y = world_to_screen(
            simulation.state.position_m,
            self.origin_px,
            self.pixels_per_metre,
        )
        pygame.draw.polygon(
            surface,
            (245, 214, 96),
            [(rocket_x, rocket_y - 12), (rocket_x - 6, rocket_y + 8), (rocket_x + 6, rocket_y + 8)],
        )

        self._draw_telemetry(surface, simulation)

    def _draw_telemetry(self, surface: pygame.Surface, simulation: Simulation) -> None:
        state = simulation.state
        if state.phase is FlightPhase.READY:
            status = "READY"
        elif state.phase is FlightPhase.LANDED:
            status = "LANDED"
        elif simulation.is_paused:
            status = f"PAUSED / {state.phase.value.upper()}"
        else:
            status = state.phase.value.upper()

        rows = (
            "SPACE launch/pause  |  R reset  |  ESC exit",
            f"Phase: {status}",
            f"Time: {state.time_s:7.3f} s",
            f"Position: ({state.position_m.x:7.3f}, {state.position_m.y:7.3f}) m",
            f"Velocity: ({state.velocity_m_s.x:7.3f}, {state.velocity_m_s.y:7.3f}) m/s",
            f"Speed: {state.velocity_m_s.magnitude:7.3f} m/s",
            f"Acceleration: ({state.acceleration_m_s2.x:7.3f}, {state.acceleration_m_s2.y:7.3f}) m/s²",
            f"Mass: {state.mass_kg:7.3f} kg",
            f"Thrust: {simulation.current_thrust_n:7.3f} N",
        )
        for index, text in enumerate(rows):
            rendered = self._font.render(text, True, (232, 238, 247))
            surface.blit(rendered, (18, 16 + index * 25))
