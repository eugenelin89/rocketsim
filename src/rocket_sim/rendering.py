"""Pygame presentation for RocketSim world state and physical forces."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import pygame

from .config import Vector2
from .physics import ForceBreakdown
from .simulation import FlightPhase, Simulation


FORCE_COLORS: dict[str, tuple[int, int, int]] = {
    "Thrust": (255, 174, 66),
    "Gravity": (106, 168, 255),
    "Drag": (238, 112, 214),
    "Net": (102, 221, 154),
}

CONTROL_ROWS = (
    "SPACE launch/pause  RIGHT single-step  R reset  ESC exit",
    "F force vectors  I Physics Inspector",
)


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


def force_vector_endpoint(
    origin_px: tuple[int, int],
    force_n: Vector2,
    pixels_per_newton: float,
) -> tuple[int, int]:
    """Map one world-frame force to a screen endpoint for drawing only."""

    return (
        round(origin_px[0] + force_n.x * pixels_per_newton),
        round(origin_px[1] - force_n.y * pixels_per_newton),
    )


def physics_inspector_rows(
    simulation: Simulation, forces: ForceBreakdown
) -> tuple[str, ...]:
    """Format inspector values from the production force breakdown."""

    state = simulation.state
    if state.phase is FlightPhase.READY:
        phase = "READY (forces inactive)"
    elif state.phase is FlightPhase.LANDED:
        phase = (
            "LANDED / impact state"
            if state.has_lifted_off
            else "NO LIFTOFF / terminal initial state"
        )
    elif simulation.is_paused:
        phase = f"PAUSED / {state.phase.value.upper()}"
    else:
        phase = state.phase.value.upper()

    if state.phase is FlightPhase.READY:
        burnout = f"pending at {simulation.config.burn_time_s:.3f} s"
    elif state.time_s >= simulation.config.burn_time_s:
        burnout = f"complete at {simulation.config.burn_time_s:.3f} s"
    else:
        burnout = f"pending at {simulation.config.burn_time_s:.3f} s"

    def force_row(name: str, force: Vector2) -> str:
        return (
            f"{name:<7} ({force.x:7.3f}, {force.y:7.3f}) N"
            f"  |F|={force.magnitude:7.3f}"
        )

    return (
        "PHYSICS INSPECTOR",
        "",
        f"Phase: {phase}",
        f"Burnout: {burnout}",
        f"Time: {state.time_s:7.3f} s",
        f"Position: ({state.position_m.x:7.3f}, {state.position_m.y:7.3f}) m",
        f"Velocity: ({state.velocity_m_s.x:7.3f}, {state.velocity_m_s.y:7.3f}) m/s",
        f"Speed: {state.velocity_m_s.magnitude:7.3f} m/s",
        (
            "Acceleration: "
            f"({state.acceleration_m_s2.x:7.3f}, "
            f"{state.acceleration_m_s2.y:7.3f}) m/s^2"
        ),
        f"Mass: {state.mass_kg:7.3f} kg",
        "",
        "FORCES",
        force_row("Thrust", forces.thrust_n),
        force_row("Gravity", forces.gravity_n),
        force_row("Drag", forces.drag_n),
        force_row("Net", forces.net_n),
        "",
        "PARAMETERS (constant)",
        f"rho: {simulation.config.air_density_kg_m3:.4f} kg/m^3",
        f"Cd: {simulation.config.drag_coefficient:.4f}",
        f"Area: {simulation.config.reference_area_m2:.4f} m^2",
        "",
        "EQUATIONS",
        "Fg = (0, -m g)",
        "Ft = T(cos(theta), sin(theta))",
        "Fd = -0.5 rho Cd A |v_air| v_air",
        "Fnet = Ft + Fg + Fd",
        "a = Fnet / m",
        "Still air: v_air = v_rocket",
    )


@dataclass(slots=True)
class Renderer:
    width_px: int = 1200
    height_px: int = 720
    pixels_per_metre: float = 20.0
    ground_y_px: int = 650
    world_width_px: int = 800
    force_pixels_per_newton: float = 5.0
    show_force_vectors: bool = True
    show_inspector: bool = True
    _font: pygame.font.Font = field(init=False, repr=False)
    _small_font: pygame.font.Font = field(init=False, repr=False)
    _heading_font: pygame.font.Font = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._font = pygame.font.Font(None, 24)
        self._small_font = pygame.font.Font(None, 18)
        self._heading_font = pygame.font.Font(None, 28)

    @property
    def origin_px(self) -> tuple[float, float]:
        return (self.world_width_px / 2.0, float(self.ground_y_px))

    def toggle_force_vectors(self) -> None:
        self.show_force_vectors = not self.show_force_vectors

    def toggle_inspector(self) -> None:
        self.show_inspector = not self.show_inspector

    def draw(self, surface: pygame.Surface, simulation: Simulation) -> None:
        surface.fill((12, 20, 36))
        pygame.draw.rect(
            surface,
            (52, 83, 55),
            pygame.Rect(
                0,
                self.ground_y_px,
                self.world_width_px,
                self.height_px - self.ground_y_px,
            ),
        )
        pygame.draw.line(
            surface,
            (142, 174, 125),
            (0, self.ground_y_px),
            (self.world_width_px, self.ground_y_px),
            2,
        )
        pygame.draw.line(
            surface,
            (86, 102, 126),
            (self.world_width_px, 0),
            (self.world_width_px, self.height_px),
            2,
        )

        self._draw_trajectory(surface, simulation)
        rocket_position = world_to_screen(
            simulation.state.position_m,
            self.origin_px,
            self.pixels_per_metre,
        )
        self._draw_rocket(surface, rocket_position)

        forces = simulation.current_forces
        if self.show_force_vectors:
            self._draw_force_vectors(surface, rocket_position, forces)

        self._draw_world_status(surface, simulation)
        if self.show_inspector:
            self._draw_inspector(surface, simulation, forces)
        else:
            rendered = self._font.render(
                "Physics Inspector hidden - press I", True, (182, 194, 211)
            )
            surface.blit(rendered, (self.world_width_px + 20, 22))

    def _draw_trajectory(
        self, surface: pygame.Surface, simulation: Simulation
    ) -> None:
        samples = simulation.trajectory
        for before, after in zip(samples, samples[1:], strict=False):
            color = (
                (255, 174, 66)
                if before.phase is FlightPhase.POWERED
                else (96, 184, 255)
            )
            pygame.draw.line(
                surface,
                color,
                world_to_screen(
                    before.position_m, self.origin_px, self.pixels_per_metre
                ),
                world_to_screen(
                    after.position_m, self.origin_px, self.pixels_per_metre
                ),
                2,
            )

    def _draw_rocket(
        self, surface: pygame.Surface, position_px: tuple[int, int]
    ) -> None:
        rocket_x, rocket_y = position_px
        pygame.draw.polygon(
            surface,
            (245, 214, 96),
            [
                (rocket_x, rocket_y - 12),
                (rocket_x - 6, rocket_y + 8),
                (rocket_x + 6, rocket_y + 8),
            ],
        )

    def _draw_force_vectors(
        self,
        surface: pygame.Surface,
        origin_px: tuple[int, int],
        forces: ForceBreakdown,
    ) -> None:
        entries = (
            ("Thrust", forces.thrust_n, -36, (-82, -8)),
            ("Gravity", forces.gravity_n, -12, (-92, -8)),
            ("Drag", forces.drag_n, 12, (5, -8)),
            ("Net", forces.net_n, 36, (5, -8)),
        )
        for name, force, origin_offset_x, label_offset in entries:
            arrow_origin = (origin_px[0] + origin_offset_x, origin_px[1])
            self._draw_force_arrow(
                surface,
                arrow_origin,
                force,
                name,
                FORCE_COLORS[name],
                label_offset,
            )

    def _draw_force_arrow(
        self,
        surface: pygame.Surface,
        origin_px: tuple[int, int],
        force_n: Vector2,
        label: str,
        color: tuple[int, int, int],
        label_offset_px: tuple[int, int],
    ) -> None:
        if force_n.magnitude == 0.0:
            return
        endpoint = force_vector_endpoint(
            origin_px, force_n, self.force_pixels_per_newton
        )
        pygame.draw.line(surface, color, origin_px, endpoint, 3)

        angle = math.atan2(endpoint[1] - origin_px[1], endpoint[0] - origin_px[0])
        arrow_size = 8.0
        left = (
            endpoint[0] - arrow_size * math.cos(angle - math.pi / 6.0),
            endpoint[1] - arrow_size * math.sin(angle - math.pi / 6.0),
        )
        right = (
            endpoint[0] - arrow_size * math.cos(angle + math.pi / 6.0),
            endpoint[1] - arrow_size * math.sin(angle + math.pi / 6.0),
        )
        pygame.draw.polygon(surface, color, [endpoint, left, right])
        rendered = self._small_font.render(
            f"{label} {force_n.magnitude:.2f} N", True, color
        )
        surface.blit(
            rendered,
            (
                endpoint[0] + label_offset_px[0],
                endpoint[1] + label_offset_px[1],
            ),
        )

    def _draw_world_status(
        self, surface: pygame.Surface, simulation: Simulation
    ) -> None:
        state = simulation.state
        if state.phase is FlightPhase.READY:
            phase = "READY"
        elif state.phase is FlightPhase.LANDED:
            phase = "LANDED"
        elif simulation.is_paused:
            phase = f"PAUSED / {state.phase.value.upper()}"
        else:
            phase = state.phase.value.upper()

        rows = (
            *CONTROL_ROWS,
            f"Phase: {phase}    t={state.time_s:.3f} s",
        )
        for index, text in enumerate(rows):
            rendered = self._font.render(text, True, (232, 238, 247))
            surface.blit(rendered, (18, 16 + index * 25))

    def _draw_inspector(
        self,
        surface: pygame.Surface,
        simulation: Simulation,
        forces: ForceBreakdown,
    ) -> None:
        panel_x = self.world_width_px + 18
        rows = physics_inspector_rows(simulation, forces)
        for index, text in enumerate(rows):
            if index == 0:
                rendered = self._heading_font.render(text, True, (245, 214, 96))
            elif text in {"FORCES", "PARAMETERS (constant)", "EQUATIONS"}:
                rendered = self._font.render(text, True, (142, 203, 255))
            else:
                rendered = self._small_font.render(text, True, (232, 238, 247))
            surface.blit(rendered, (panel_x, 16 + index * 23))
