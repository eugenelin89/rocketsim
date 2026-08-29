"""Validated configuration and neutral vector types for the simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

from .propulsion import DEFAULT_EDUCATIONAL_THRUST_CURVE, ThrustCurve


@dataclass(frozen=True, slots=True)
class Vector2:
    """A small Pygame-independent two-dimensional vector."""

    x: float
    y: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.x) or not math.isfinite(self.y):
            raise ValueError("vector components must be finite")

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2:
        return self * scalar

    @property
    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)


def _require_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Physical parameters for one deterministic sampled-thrust run."""

    mass_kg: float = 1.0
    thrust_curve: ThrustCurve = field(
        default_factory=lambda: DEFAULT_EDUCATIONAL_THRUST_CURVE
    )
    launch_angle_rad: float = math.pi / 2.0
    gravity_m_s2: float = 9.81
    air_density_kg_m3: float = 1.225
    drag_coefficient: float = 0.75
    reference_area_m2: float = 0.01
    physics_dt_s: float = 0.01
    initial_position_m: Vector2 = field(default_factory=lambda: Vector2(0.0, 0.0))
    initial_velocity_m_s: Vector2 = field(default_factory=lambda: Vector2(0.0, 0.0))

    def __post_init__(self) -> None:
        scalar_values = {
            "mass_kg": self.mass_kg,
            "launch_angle_rad": self.launch_angle_rad,
            "gravity_m_s2": self.gravity_m_s2,
            "air_density_kg_m3": self.air_density_kg_m3,
            "drag_coefficient": self.drag_coefficient,
            "reference_area_m2": self.reference_area_m2,
            "physics_dt_s": self.physics_dt_s,
        }
        for name, value in scalar_values.items():
            _require_finite(name, value)

        if self.mass_kg <= 0.0:
            raise ValueError("mass_kg must be greater than zero")
        if self.physics_dt_s <= 0.0:
            raise ValueError("physics_dt_s must be greater than zero")
        if not isinstance(self.thrust_curve, ThrustCurve):
            raise TypeError("thrust_curve must be a ThrustCurve")
        if self.gravity_m_s2 < 0.0:
            raise ValueError("gravity_m_s2 must be non-negative")
        if self.air_density_kg_m3 < 0.0:
            raise ValueError("air_density_kg_m3 must be non-negative")
        if self.drag_coefficient < 0.0:
            raise ValueError("drag_coefficient must be non-negative")
        if self.reference_area_m2 < 0.0:
            raise ValueError("reference_area_m2 must be non-negative")
        if self.initial_position_m.y < 0.0:
            raise ValueError("initial altitude must be at or above ground")
