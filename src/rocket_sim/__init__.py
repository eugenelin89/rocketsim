"""Pygame rocket simulator package."""

from .config import SimulationConfig, Vector2
from .physics import ForceBreakdown
from .simulation import FlightPhase, RocketState, Simulation

__version__ = "0.1.0"

__all__ = [
    "FlightPhase",
    "ForceBreakdown",
    "RocketState",
    "Simulation",
    "SimulationConfig",
    "Vector2",
    "__version__",
]
