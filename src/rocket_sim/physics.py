"""Pygame-independent force and integration functions."""

from __future__ import annotations

import math

from .config import SimulationConfig, Vector2


def gravity_force_n(mass_kg: float, gravity_m_s2: float) -> Vector2:
    """Return the constant downward gravitational force in newtons."""

    return Vector2(0.0, -mass_kg * gravity_m_s2)


def thrust_force_n(config: SimulationConfig, time_s: float) -> Vector2:
    """Return constant world-angle thrust on the half-open burn interval."""

    if not math.isfinite(time_s):
        raise ValueError("time_s must be finite")
    if not 0.0 <= time_s < config.burn_time_s:
        return Vector2(0.0, 0.0)
    return Vector2(
        config.thrust_n * math.cos(config.launch_angle_rad),
        config.thrust_n * math.sin(config.launch_angle_rad),
    )


def acceleration_m_s2(config: SimulationConfig, time_s: float) -> Vector2:
    """Return net acceleration from thrust and gravity at ``time_s``."""

    thrust = thrust_force_n(config, time_s)
    gravity = gravity_force_n(config.mass_kg, config.gravity_m_s2)
    return (thrust + gravity) * (1.0 / config.mass_kg)


def semi_implicit_euler(
    position_m: Vector2,
    velocity_m_s: Vector2,
    acceleration: Vector2,
    duration_s: float,
) -> tuple[Vector2, Vector2]:
    """Advance one constant-acceleration segment using updated velocity."""

    if not math.isfinite(duration_s) or duration_s <= 0.0:
        raise ValueError("duration_s must be finite and greater than zero")
    new_velocity = velocity_m_s + acceleration * duration_s
    new_position = position_m + new_velocity * duration_s
    return new_position, new_velocity
