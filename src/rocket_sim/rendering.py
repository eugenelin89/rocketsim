"""Pygame presentation for RocketSim world state and physical forces."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import pygame

from .config import Vector2
from .physics import ForceBreakdown
from .propulsion import ThrustCurve
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


@dataclass(frozen=True, slots=True)
class ThrustTimelineGeometry:
    """Rendering-only coordinates derived from one production thrust curve."""

    sample_points_px: tuple[tuple[int, int], ...]
    cursor_x_px: int
    burnout_x_px: int
    current_thrust_n: float
    cursor_time_s: float
    burnout_zero_point_px: tuple[int, int]
    terminal_sample_is_left_limit: bool


def thrust_timeline_geometry(
    thrust_curve: ThrustCurve,
    current_time_s: float,
    current_thrust_n: float,
    graph_rect: pygame.Rect,
) -> ThrustTimelineGeometry:
    """Map production samples and current motor time into a graph rectangle."""

    burn_duration_s = thrust_curve.burn_duration_s
    peak_thrust_n = thrust_curve.peak_thrust_n
    cursor_time_s = min(max(current_time_s, 0.0), burn_duration_s)

    def time_x(time_s: float) -> int:
        if burn_duration_s == 0.0:
            return graph_rect.left
        return round(
            graph_rect.left + graph_rect.width * time_s / burn_duration_s
        )

    def thrust_y(thrust_n: float) -> int:
        if peak_thrust_n == 0.0:
            return graph_rect.bottom
        return round(
            graph_rect.bottom - graph_rect.height * thrust_n / peak_thrust_n
        )

    return ThrustTimelineGeometry(
        sample_points_px=tuple(
            (time_x(sample.time_s), thrust_y(sample.thrust_n))
            for sample in thrust_curve.samples
        ),
        cursor_x_px=time_x(cursor_time_s),
        burnout_x_px=time_x(burn_duration_s),
        current_thrust_n=current_thrust_n,
        cursor_time_s=cursor_time_s,
        burnout_zero_point_px=(time_x(burn_duration_s), thrust_y(0.0)),
        terminal_sample_is_left_limit=(
            burn_duration_s > 0.0 and thrust_curve.samples[-1].thrust_n > 0.0
        ),
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

    thrust_curve = simulation.config.thrust_curve
    if thrust_curve.burn_duration_s == 0.0:
        burnout = "zero-duration curve (no burn)"
        motor_phase = (
            "READY / NO BURN"
            if state.phase is FlightPhase.READY
            else "COMPLETE / NO BURN"
        )
    elif state.phase is FlightPhase.READY:
        burnout = (
            f"pending at {thrust_curve.burn_duration_s:.3f} s"
        )
        motor_phase = "READY"
    elif state.time_s >= thrust_curve.burn_duration_s:
        burnout = (
            f"complete at {thrust_curve.burn_duration_s:.3f} s"
        )
        motor_phase = "COMPLETE"
    else:
        burnout = (
            f"pending at {thrust_curve.burn_duration_s:.3f} s"
        )
        motor_phase = (
            "ACTIVE (flight terminal)"
            if state.phase is FlightPhase.LANDED
            else "ACTIVE"
        )

    if thrust_curve.burn_duration_s == 0.0:
        burn_progress = "N/A (zero-duration)"
    else:
        fraction = min(
            max(state.time_s / thrust_curve.burn_duration_s, 0.0), 1.0
        )
        burn_progress = f"{100.0 * fraction:6.2f}%"

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
        "MOTOR",
        f"Motor phase: {motor_phase}",
        f"Current thrust: {forces.thrust_n.magnitude:7.3f} N",
        f"Burn-time progress: {burn_progress}",
        f"Burn duration: {thrust_curve.burn_duration_s:7.3f} s",
        f"Peak stored thrust: {thrust_curve.peak_thrust_n:7.3f} N",
        f"Average thrust: {thrust_curve.average_thrust_n:7.3f} N",
        f"Delivered impulse: {simulation.delivered_impulse_ns:7.3f} N*s",
        f"Total impulse: {thrust_curve.total_impulse_ns:7.3f} N*s",
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
        "Ft(t) = T(t) (cos(theta), sin(theta))",
        "Fd = -0.5 rho Cd A |v_air| v_air",
        "Fnet = Ft + Fg + Fd",
        "a = Fnet / m",
        "I = integral T(t) dt",
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
        forces = simulation.current_forces
        self._draw_thrust_timeline(
            surface, simulation, forces.thrust_n.magnitude
        )
        rocket_position = world_to_screen(
            simulation.state.position_m,
            self.origin_px,
            self.pixels_per_metre,
        )
        self._draw_rocket(surface, rocket_position)

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

    def _draw_thrust_timeline(
        self,
        surface: pygame.Surface,
        simulation: Simulation,
        current_thrust_n: float,
    ) -> None:
        panel = pygame.Rect(self.world_width_px - 374, 82, 352, 184)
        graph = pygame.Rect(panel.left + 42, panel.top + 30, 290, 118)
        curve = simulation.config.thrust_curve
        geometry = thrust_timeline_geometry(
            curve, simulation.state.time_s, current_thrust_n, graph
        )

        pygame.draw.rect(surface, (18, 31, 53), panel, border_radius=6)
        pygame.draw.rect(surface, (78, 98, 126), panel, 1, border_radius=6)
        pygame.draw.line(
            surface,
            (145, 159, 181),
            (graph.left, graph.bottom),
            (graph.right, graph.bottom),
            1,
        )
        pygame.draw.line(
            surface,
            (145, 159, 181),
            (graph.left, graph.top),
            (graph.left, graph.bottom),
            1,
        )

        pygame.draw.line(
            surface,
            (238, 112, 214),
            (geometry.burnout_x_px, graph.top),
            (geometry.burnout_x_px, graph.bottom),
            1,
        )

        if len(geometry.sample_points_px) > 1:
            pygame.draw.lines(
                surface,
                (255, 174, 66),
                False,
                geometry.sample_points_px,
                2,
            )
        filled_points = geometry.sample_points_px
        if geometry.terminal_sample_is_left_limit:
            filled_points = geometry.sample_points_px[:-1]
        for point in filled_points:
            pygame.draw.circle(surface, (245, 214, 96), point, 3)
        if geometry.terminal_sample_is_left_limit:
            terminal_point = geometry.sample_points_px[-1]
            pygame.draw.circle(surface, (18, 31, 53), terminal_point, 4)
            pygame.draw.circle(surface, (245, 214, 96), terminal_point, 4, 1)
            pygame.draw.circle(
                surface, (245, 214, 96), geometry.burnout_zero_point_px, 3
            )
        pygame.draw.line(
            surface,
            (102, 221, 154),
            (geometry.cursor_x_px, graph.top),
            (geometry.cursor_x_px, graph.bottom),
            2,
        )

        heading = self._small_font.render(
            "MOTOR THRUST TIMELINE", True, (245, 214, 96)
        )
        surface.blit(heading, (panel.left + 10, panel.top + 7))
        labels = (
            ("T (N)", (panel.left + 5, graph.top - 2)),
            (
                f"motor cursor {geometry.cursor_time_s:.3f} s"
                + (
                    " (clamped at burnout)"
                    if simulation.state.time_s > curve.burn_duration_s
                    else ""
                ),
                (panel.left + 10, graph.bottom + 7),
            ),
            (
                f"T={geometry.current_thrust_n:.2f} N  stored peak={curve.peak_thrust_n:.2f} N",
                (panel.left + 190, panel.top + 7),
            ),
            ("t (s)", (graph.right - 26, graph.bottom - 17)),
        )
        for label, position in labels:
            rendered = self._small_font.render(label, True, (213, 222, 236))
            surface.blit(rendered, position)

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
            elif text in {
                "MOTOR",
                "FORCES",
                "PARAMETERS (constant)",
                "EQUATIONS",
            }:
                rendered = self._font.render(text, True, (142, 203, 255))
            else:
                rendered = self._small_font.render(text, True, (232, 238, 247))
            surface.blit(rendered, (panel_x, 12 + index * 17))
