"""Pygame-independent force and integration functions."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .config import SimulationConfig, Vector2


@dataclass(frozen=True, slots=True)
class ForceBreakdown:
    """Named physical forces evaluated for one instantaneous state."""

    thrust_n: Vector2
    gravity_n: Vector2
    drag_n: Vector2
    net_n: Vector2

    @classmethod
    def zero(cls) -> ForceBreakdown:
        zero = Vector2(0.0, 0.0)
        return cls(thrust_n=zero, gravity_n=zero, drag_n=zero, net_n=zero)


def gravity_force_n(mass_kg: float, gravity_m_s2: float) -> Vector2:
    """Return the constant downward gravitational force in newtons."""

    return Vector2(0.0, -mass_kg * gravity_m_s2)


def thrust_force_n(config: SimulationConfig, time_s: float) -> Vector2:
    """Return instantaneous sampled thrust at the fixed world angle."""

    if not math.isfinite(time_s):
        raise ValueError("time_s must be finite")
    thrust_n = config.thrust_curve.thrust_at(time_s)
    return Vector2(
        thrust_n * math.cos(config.launch_angle_rad),
        thrust_n * math.sin(config.launch_angle_rad),
    )


def thrust_impulse_n_s(
    config: SimulationConfig, start_time_s: float, end_time_s: float
) -> Vector2:
    """Return exact motor impulse over an interval at the fixed direction."""

    impulse_ns = config.thrust_curve.impulse_between_ns(start_time_s, end_time_s)
    return Vector2(
        impulse_ns * math.cos(config.launch_angle_rad),
        impulse_ns * math.sin(config.launch_angle_rad),
    )


def drag_force_n(
    config: SimulationConfig, air_relative_velocity_m_s: Vector2
) -> Vector2:
    """Return constant-property quadratic drag in still air."""

    speed_m_s = air_relative_velocity_m_s.magnitude
    if (
        speed_m_s == 0.0
        or config.air_density_kg_m3 == 0.0
        or config.drag_coefficient == 0.0
        or config.reference_area_m2 == 0.0
    ):
        return Vector2(0.0, 0.0)

    scale = (
        -0.5
        * config.air_density_kg_m3
        * config.drag_coefficient
        * config.reference_area_m2
        * speed_m_s
    )
    return air_relative_velocity_m_s * scale


def force_breakdown_n(
    config: SimulationConfig,
    time_s: float,
    air_relative_velocity_m_s: Vector2,
) -> ForceBreakdown:
    """Return thrust, gravity, drag, and their exact vector sum."""

    thrust = thrust_force_n(config, time_s)
    gravity = gravity_force_n(config.mass_kg, config.gravity_m_s2)
    drag = drag_force_n(config, air_relative_velocity_m_s)
    return ForceBreakdown(
        thrust_n=thrust,
        gravity_n=gravity,
        drag_n=drag,
        net_n=thrust + gravity + drag,
    )


def acceleration_m_s2(
    config: SimulationConfig,
    time_s: float,
    air_relative_velocity_m_s: Vector2,
) -> Vector2:
    """Return acceleration from the instantaneous force breakdown."""

    forces = force_breakdown_n(config, time_s, air_relative_velocity_m_s)
    return forces.net_n * (1.0 / config.mass_kg)


def semi_implicit_euler(
    position_m: Vector2,
    velocity_m_s: Vector2,
    acceleration: Vector2,
    duration_s: float,
) -> tuple[Vector2, Vector2]:
    """Advance one force-frozen segment using updated velocity."""

    if not math.isfinite(duration_s) or duration_s <= 0.0:
        raise ValueError("duration_s must be finite and greater than zero")
    new_velocity = velocity_m_s + acceleration * duration_s
    new_position = position_m + new_velocity * duration_s
    return new_position, new_velocity


def semi_implicit_impulse_step(
    position_m: Vector2,
    velocity_m_s: Vector2,
    thrust_impulse_ns: Vector2,
    other_force_n: Vector2,
    mass_kg: float,
    duration_s: float,
) -> tuple[Vector2, Vector2]:
    """Advance using exact thrust impulse and start-state non-thrust force."""

    if not math.isfinite(mass_kg) or mass_kg <= 0.0:
        raise ValueError("mass_kg must be finite and greater than zero")
    if not math.isfinite(duration_s) or duration_s <= 0.0:
        raise ValueError("duration_s must be finite and greater than zero")
    total_impulse_ns = thrust_impulse_ns + other_force_n * duration_s
    new_velocity = velocity_m_s + total_impulse_ns * (1.0 / mass_kg)
    new_position = position_m + new_velocity * duration_s
    return new_position, new_velocity
