"""Pygame-independent pre-launch setup definitions and config rebuilding."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import math

from .config import SimulationConfig


class SetupParameter(str, Enum):
    """Physical parameters exposed by the educational READY-state controls."""

    MASS = "mass_kg"
    LAUNCH_ANGLE = "launch_angle_rad"
    DRAG_COEFFICIENT = "drag_coefficient"
    REFERENCE_AREA = "reference_area_m2"
    AIR_DENSITY = "air_density_kg_m3"
    GRAVITY = "gravity_m_s2"


@dataclass(frozen=True, slots=True)
class SetupParameterSpec:
    """Presentation bounds and formatting for one editable setup parameter."""

    parameter: SetupParameter
    group: str
    label: str
    unit: str
    minimum: float
    maximum: float
    step: float
    decimal_places: int


SETUP_PARAMETER_SPECS = (
    SetupParameterSpec(
        SetupParameter.MASS,
        "ROCKET",
        "Mass (constant/run)",
        "kg",
        0.1,
        10.0,
        0.1,
        2,
    ),
    SetupParameterSpec(
        SetupParameter.LAUNCH_ANGLE,
        "LAUNCH",
        "Fixed thrust direction",
        "deg",
        10.0,
        90.0,
        5.0,
        0,
    ),
    SetupParameterSpec(
        SetupParameter.DRAG_COEFFICIENT,
        "AERODYNAMICS",
        "Drag coefficient Cd",
        "",
        0.0,
        2.0,
        0.05,
        2,
    ),
    SetupParameterSpec(
        SetupParameter.REFERENCE_AREA,
        "AERODYNAMICS",
        "Reference area",
        "m^2",
        0.001,
        0.100,
        0.001,
        3,
    ),
    SetupParameterSpec(
        SetupParameter.AIR_DENSITY,
        "ENVIRONMENT",
        "Air density",
        "kg/m^3",
        0.0,
        2.0,
        0.05,
        3,
    ),
    SetupParameterSpec(
        SetupParameter.GRAVITY,
        "ENVIRONMENT",
        "Gravity",
        "m/s^2",
        0.0,
        20.0,
        0.25,
        2,
    ),
)

_SPEC_BY_PARAMETER = {
    spec.parameter: spec for spec in SETUP_PARAMETER_SPECS
}


class AppActionKind(str, Enum):
    """Application commands shared by keyboard and mouse input paths."""

    EXIT = "exit"
    PRIMARY = "primary"
    RESET_FLIGHT = "reset_flight"
    RESTORE_DEFAULTS = "restore_defaults"
    SINGLE_STEP = "single_step"
    TOGGLE_FORCE_VECTORS = "toggle_force_vectors"
    TOGGLE_INSPECTOR = "toggle_inspector"
    ADJUST_SETUP = "adjust_setup"


@dataclass(frozen=True, slots=True)
class AppAction:
    """One typed learner or application action."""

    kind: AppActionKind
    parameter: SetupParameter | None = None
    direction: int = 0

    def __post_init__(self) -> None:
        if self.kind is AppActionKind.ADJUST_SETUP:
            if self.parameter is None or self.direction not in (-1, 1):
                raise ValueError(
                    "setup adjustment requires a parameter and +/-1 direction"
                )
        elif self.parameter is not None or self.direction != 0:
            raise ValueError(
                "only setup-adjustment actions carry a parameter or direction"
            )


@dataclass(frozen=True, slots=True)
class SetupDisplayRow:
    """One rendered setup label/value pair sourced from production config."""

    parameter: SetupParameter
    group: str
    label: str
    value: str


def setup_parameter_spec(parameter: SetupParameter) -> SetupParameterSpec:
    """Return the one authoritative UI specification for a setup parameter."""

    return _SPEC_BY_PARAMETER[parameter]


def setup_display_value(
    config: SimulationConfig, parameter: SetupParameter
) -> float:
    """Return the learner-facing value, converting only angle to degrees."""

    value = getattr(config, parameter.value)
    if parameter is SetupParameter.LAUNCH_ANGLE:
        return math.degrees(value)
    return value


def setup_display_rows(config: SimulationConfig) -> tuple[SetupDisplayRow, ...]:
    """Format all displayed values directly from the production configuration."""

    rows = []
    for spec in SETUP_PARAMETER_SPECS:
        number = setup_display_value(config, spec.parameter)
        formatted = f"{number:.{spec.decimal_places}f}"
        if spec.unit:
            formatted = f"{formatted} {spec.unit}"
        rows.append(
            SetupDisplayRow(
                parameter=spec.parameter,
                group=spec.group,
                label=spec.label,
                value=formatted,
            )
        )
    return tuple(rows)


def adjusted_setup_config(
    config: SimulationConfig,
    parameter: SetupParameter,
    direction: int,
) -> SimulationConfig:
    """Return a validated config after one current-value-relative UI step.

    Bounds belong only to the educational interface. Off-grid production
    defaults such as rho=1.225 and g=9.81 remain unchanged until clicked, and a
    plus/minus pair returns to the original displayed value without grid snap.
    """

    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or 1")

    spec = setup_parameter_spec(parameter)
    current = setup_display_value(config, parameter)
    stepped = round(
        current + direction * spec.step,
        spec.decimal_places,
    )
    bounded = min(max(stepped, spec.minimum), spec.maximum)
    if bounded == current:
        return config

    physical_value = (
        math.radians(bounded)
        if parameter is SetupParameter.LAUNCH_ANGLE
        else bounded
    )
    return replace(config, **{parameter.value: physical_value})
