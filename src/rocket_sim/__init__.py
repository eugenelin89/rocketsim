"""Pygame rocket simulator package."""

from .config import SimulationConfig, Vector2
from .physics import ForceBreakdown
from .missions import (
    FlightOutcome,
    FlightResult,
    MISSIONS,
    Mission,
    MissionEvaluation,
)
from .propulsion import (
    DEFAULT_EDUCATIONAL_THRUST_CURVE,
    ThrustCurve,
    ThrustSample,
)
from .simulation import FlightPhase, RocketState, Simulation

__version__ = "0.1.0"

__all__ = [
    "FlightPhase",
    "FlightOutcome",
    "FlightResult",
    "ForceBreakdown",
    "DEFAULT_EDUCATIONAL_THRUST_CURVE",
    "RocketState",
    "MISSIONS",
    "Mission",
    "MissionEvaluation",
    "Simulation",
    "SimulationConfig",
    "ThrustCurve",
    "ThrustSample",
    "Vector2",
    "__version__",
]
