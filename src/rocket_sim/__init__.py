"""Pygame rocket simulator package."""

from .config import SimulationConfig, Vector2
from .physics import ForceBreakdown
from .propulsion import (
    DEFAULT_EDUCATIONAL_THRUST_CURVE,
    ThrustCurve,
    ThrustSample,
)
from .simulation import FlightPhase, RocketState, Simulation

__version__ = "0.1.0"

__all__ = [
    "FlightPhase",
    "ForceBreakdown",
    "DEFAULT_EDUCATIONAL_THRUST_CURVE",
    "RocketState",
    "Simulation",
    "SimulationConfig",
    "ThrustCurve",
    "ThrustSample",
    "Vector2",
    "__version__",
]
