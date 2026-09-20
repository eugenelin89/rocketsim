"""Pygame-independent completed-flight metrics and explicit mission rules."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import math

from .config import SimulationConfig
from .physics import drag_force_n
from .setup import SetupParameter
from .simulation import FlightPhase, Simulation


class FlightOutcome(str, Enum):
    """Terminal outcomes represented by the current production simulation."""

    NO_LIFTOFF = "no_liftoff"
    LANDED = "landed"


@dataclass(frozen=True, slots=True)
class FlightResult:
    """Immutable recorded metrics extracted from one completed production run.

    Extrema are maxima over recorded production states.  They are not claimed
    to be exact continuous-trajectory extrema.  Impact speed is the magnitude
    of the pre-contact ground-frame velocity, not an impact deceleration.
    """

    outcome: FlightOutcome
    config: SimulationConfig
    apogee_m: float
    landing_x_m: float | None
    impact_speed_m_s: float | None
    max_speed_m_s: float
    max_acceleration_m_s2: float
    max_drag_n: float
    flight_time_s: float
    liftoff_occurred: bool

    @property
    def configured_mass_kg(self) -> float:
        """Return the run's total constant vehicle mass."""

        return self.config.mass_kg

    @classmethod
    def from_simulation(cls, simulation: Simulation) -> FlightResult:
        """Snapshot a terminal simulation without mutating it."""

        if not simulation.is_finished:
            raise ValueError("a FlightResult requires a terminal simulation")

        config = simulation.config
        terminal = simulation.state
        trajectory = simulation.trajectory
        if terminal.phase is not FlightPhase.LANDED or trajectory[-1] != terminal:
            raise ValueError("terminal state and trajectory are inconsistent")

        lifted_off = terminal.has_lifted_off
        outcome = FlightOutcome.LANDED if lifted_off else FlightOutcome.NO_LIFTOFF
        return cls(
            outcome=outcome,
            config=config,
            apogee_m=max(state.position_m.y for state in trajectory),
            landing_x_m=terminal.position_m.x if lifted_off else None,
            impact_speed_m_s=(
                terminal.velocity_m_s.magnitude if lifted_off else None
            ),
            max_speed_m_s=max(
                state.velocity_m_s.magnitude for state in trajectory
            ),
            max_acceleration_m_s2=max(
                state.acceleration_m_s2.magnitude for state in trajectory
            ),
            max_drag_n=max(
                drag_force_n(config, state.velocity_m_s).magnitude
                for state in trajectory
            ),
            flight_time_s=terminal.time_s,
            liftoff_occurred=lifted_off,
        )


class ObjectiveKind(str, Enum):
    MINIMUM_APOGEE = "minimum_apogee"
    APOGEE_BAND = "apogee_band"
    GROUND_CONTACT_ZONE = "ground_contact_zone"


@dataclass(frozen=True, slots=True)
class ObjectiveEvaluation:
    description: str
    passed: bool
    actual: str
    target: str
    feedback: str


@dataclass(frozen=True, slots=True)
class MissionObjective:
    """One explicit inclusive physical-result constraint."""

    kind: ObjectiveKind
    description: str
    lower: float
    upper: float | None = None

    def __post_init__(self) -> None:
        if not math.isfinite(self.lower):
            raise ValueError("objective lower bound must be finite")
        if self.upper is not None:
            if not math.isfinite(self.upper) or self.upper < self.lower:
                raise ValueError("objective upper bound must be finite and ordered")
        if self.kind is not ObjectiveKind.MINIMUM_APOGEE and self.upper is None:
            raise ValueError("band objectives require an upper bound")

    @property
    def target_text(self) -> str:
        if self.kind is ObjectiveKind.MINIMUM_APOGEE:
            return f"recorded apogee >= {self.lower:.1f} m"
        if self.kind is ObjectiveKind.APOGEE_BAND:
            return f"recorded apogee {self.lower:.1f}-{self.upper:.1f} m"
        return f"ground contact x = {self.lower:.1f}-{self.upper:.1f} m"

    def evaluate(self, result: FlightResult) -> ObjectiveEvaluation:
        if result.outcome is FlightOutcome.NO_LIFTOFF:
            return ObjectiveEvaluation(
                self.description,
                False,
                "NO LIFTOFF",
                self.target_text,
                "The selected configuration did not enter free flight.",
            )

        if self.kind is ObjectiveKind.MINIMUM_APOGEE:
            actual = result.apogee_m
            passed = actual >= self.lower
            feedback = (
                "Required recorded altitude reached."
                if passed
                else f"Recorded apogee was {self.lower - actual:.2f} m too low."
            )
        elif self.kind is ObjectiveKind.APOGEE_BAND:
            actual = result.apogee_m
            assert self.upper is not None
            passed = self.lower <= actual <= self.upper
            if passed:
                feedback = "Recorded apogee is inside the target band."
            elif actual < self.lower:
                feedback = f"Recorded apogee was {self.lower - actual:.2f} m too low."
            else:
                feedback = f"Recorded apogee was {actual - self.upper:.2f} m too high."
        else:
            assert self.upper is not None
            if result.landing_x_m is None:
                return ObjectiveEvaluation(
                    self.description,
                    False,
                    "unavailable",
                    self.target_text,
                    "Ground-contact position is unavailable.",
                )
            actual = result.landing_x_m
            passed = self.lower <= actual <= self.upper
            if passed:
                feedback = "Ground contact occurred inside the target zone."
            elif actual < self.lower:
                feedback = f"Ground contact was {self.lower - actual:.2f} m short."
            else:
                feedback = f"Ground contact was {actual - self.upper:.2f} m long."

        label = (
            "recorded apogee"
            if self.kind is not ObjectiveKind.GROUND_CONTACT_ZONE
            else "ground-contact x"
        )
        return ObjectiveEvaluation(
            self.description,
            passed,
            f"{label} {actual:.3f} m",
            self.target_text,
            feedback,
        )

    def live_passed(self, simulation: Simulation) -> bool | None:
        """Return a logically knowable live pass, otherwise pending."""

        if self.kind is ObjectiveKind.MINIMUM_APOGEE:
            reached = max(
                state.position_m.y for state in simulation.trajectory
            ) >= self.lower
            if reached:
                return True
            if not simulation.is_finished:
                return None
        if simulation.is_finished:
            return self.evaluate(FlightResult.from_simulation(simulation)).passed
        return None


class ScoreMetric(str, Enum):
    APOGEE_HIGH = "apogee_high"
    CONFIGURED_MASS_HIGH = "configured_mass_high"
    APOGEE_ACCURACY = "apogee_accuracy"
    CONTACT_ACCURACY = "contact_accuracy"


@dataclass(frozen=True, slots=True)
class ScoreRule:
    """Transparent 0-500 performance component for a completed objective."""

    label: str
    metric: ScoreMetric
    reference: float
    excellence: float

    @property
    def explanation(self) -> str:
        if self.metric is ScoreMetric.APOGEE_HIGH:
            return (
                f"Performance scales linearly from {self.reference:.1f} m (0) "
                f"to {self.excellence:.1f} m (500)."
            )
        if self.metric is ScoreMetric.CONFIGURED_MASS_HIGH:
            return (
                f"Performance scales linearly from {self.reference:.1f} kg (0) "
                f"to {self.excellence:.1f} kg (500)."
            )
        unit = "m"
        return (
            f"Performance falls linearly from 500 at {self.reference:.1f} {unit} "
            f"to 0 at +/-{self.excellence:.1f} {unit}."
        )

    def quality(self, result: FlightResult) -> float:
        if self.metric is ScoreMetric.APOGEE_HIGH:
            span = self.excellence - self.reference
            return (result.apogee_m - self.reference) / span
        if self.metric is ScoreMetric.CONFIGURED_MASS_HIGH:
            span = self.excellence - self.reference
            return (result.configured_mass_kg - self.reference) / span
        if self.metric is ScoreMetric.APOGEE_ACCURACY:
            half_width = self.excellence
            return 1.0 - abs(result.apogee_m - self.reference) / half_width
        if result.landing_x_m is None:
            return 0.0
        half_width = self.excellence
        return 1.0 - abs(result.landing_x_m - self.reference) / half_width

    def points(self, result: FlightResult) -> int:
        return round(500.0 * min(max(self.quality(result), 0.0), 1.0))


@dataclass(frozen=True, slots=True)
class ScoreComponent:
    label: str
    detail: str
    points: int


@dataclass(frozen=True, slots=True)
class MissionEvaluation:
    mission_id: str
    objectives: tuple[ObjectiveEvaluation, ...]
    components: tuple[ScoreComponent, ...]
    score: int
    stars: int
    success: bool


def stars_for_score(score: int) -> int:
    """Map an integer successful score onto the documented star boundaries."""

    if score < 0:
        raise ValueError("score must be non-negative")
    return 3 if score >= 900 else 2 if score >= 750 else 1 if score >= 500 else 0


@dataclass(frozen=True, slots=True)
class Mission:
    id: str
    number: int
    title: str
    description: str
    concept: str
    allowed_setup_fields: frozenset[SetupParameter]
    base_config: SimulationConfig
    objectives: tuple[MissionObjective, ...]
    score_rule: ScoreRule
    hint: str
    constraints: tuple[str, ...]

    def evaluate(self, result: FlightResult) -> MissionEvaluation:
        """Evaluate only the result's captured run and configuration."""

        objective_results = tuple(
            objective.evaluate(result) for objective in self.objectives
        )
        success = all(objective.passed for objective in objective_results)
        if success:
            performance_points = self.score_rule.points(result)
            components = (
                ScoreComponent("Mandatory objective", "complete", 500),
                ScoreComponent(
                    self.score_rule.label,
                    "physical-result performance",
                    performance_points,
                ),
            )
            score = sum(component.points for component in components)
            stars = stars_for_score(score)
        else:
            components = (
                ScoreComponent("Mandatory objective", "not complete", 0),
                ScoreComponent(self.score_rule.label, "locked", 0),
            )
            score = 0
            stars = 0
        return MissionEvaluation(
            self.id,
            objective_results,
            components,
            score,
            stars,
            success,
        )


_DEFAULT = SimulationConfig()

MISSIONS: tuple[Mission, ...] = (
    Mission(
        "first_flight",
        1,
        "First Flight",
        "Choose a constant vehicle mass that reaches the altitude objective.",
        "Mass, weight, and acceleration",
        frozenset({SetupParameter.MASS}),
        replace(_DEFAULT, mass_kg=1.1),
        (
            MissionObjective(
                ObjectiveKind.MINIMUM_APOGEE,
                "Reach at least 8.0 m recorded altitude",
                8.0,
            ),
        ),
        ScoreRule("Altitude margin", ScoreMetric.APOGEE_HIGH, 8.0, 12.0),
        (
            "The same motor accelerates the selected constant mass while gravity "
            "supplies weight. Predict how mass changes acceleration and apogee."
        ),
        ("Default motor and 0.010 s timestep are fixed.", "Gravity stays positive."),
    ),
    Mission(
        "precision_contact",
        2,
        "Precision Landing",
        "Place modeled ground contact inside the marked horizontal zone.",
        "Fixed thrust direction and vector components",
        frozenset({SetupParameter.LAUNCH_ANGLE}),
        replace(_DEFAULT, launch_angle_rad=math.radians(55.0)),
        (
            MissionObjective(
                ObjectiveKind.GROUND_CONTACT_ZONE,
                "Contact the ground inside x = 17.5-18.7 m",
                17.5,
                18.7,
            ),
        ),
        ScoreRule("Contact accuracy", ScoreMetric.CONTACT_ACCURACY, 18.1, 0.6),
        (
            "A lower fixed direction creates more horizontal thrust but less "
            "vertical thrust. It is a world-fixed force direction, not attitude."
        ),
        ("Only fixed thrust direction may change.", "No recovery/contact dynamics."),
    ),
    Mission(
        "heavy_lift",
        3,
        "Heavy Lift Challenge",
        "Use the greatest constant vehicle mass you can while clearing 3.0 m.",
        "Impulse shared across total constant mass",
        frozenset({SetupParameter.MASS}),
        replace(_DEFAULT, mass_kg=1.0),
        (
            MissionObjective(
                ObjectiveKind.MINIMUM_APOGEE,
                "Reach at least 3.0 m recorded altitude",
                3.0,
            ),
        ),
        ScoreRule(
            "Configured constant mass",
            ScoreMetric.CONFIGURED_MASS_HIGH,
            1.0,
            1.3,
        ),
        (
            "Motor impulse is unchanged. Predict how sharing its momentum change "
            "across greater constant mass affects altitude."
        ),
        ("Mass is total constant vehicle mass, not a payload model.",),
    ),
    Mission(
        "drag_tuning",
        4,
        "Aerodynamic Challenge",
        "Tune Cd so modeled ground contact falls inside a narrow target band.",
        "Quadratic drag and velocity feedback",
        frozenset({SetupParameter.DRAG_COEFFICIENT}),
        replace(
            _DEFAULT,
            launch_angle_rad=math.radians(70.0),
            drag_coefficient=1.0,
        ),
        (
            MissionObjective(
                ObjectiveKind.GROUND_CONTACT_ZONE,
                "Contact the ground inside x = 13.9-14.3 m",
                13.9,
                14.3,
            ),
        ),
        ScoreRule("Contact accuracy", ScoreMetric.CONTACT_ACCURACY, 14.1, 0.2),
        (
            "At equal speed drag scales with Cd, but drag also changes the later "
            "speed history. Use each miss to decide which direction to adjust."
        ),
        ("Direction is fixed at 70 deg.", "Density and reference area are fixed."),
    ),
    Mission(
        "low_gravity",
        5,
        "Environmental Challenge",
        "Tune mass for a 20-23 m recorded apogee in fixed low gravity.",
        "Controlled comparison of constant gravity",
        frozenset({SetupParameter.MASS}),
        replace(_DEFAULT, gravity_m_s2=3.71, mass_kg=1.0),
        (
            MissionObjective(
                ObjectiveKind.APOGEE_BAND,
                "Finish with recorded apogee between 20.0 and 23.0 m",
                20.0,
                23.0,
            ),
        ),
        ScoreRule("Altitude accuracy", ScoreMetric.APOGEE_ACCURACY, 21.5, 1.5),
        (
            "Lower constant gravity reduces modeled weight throughout the run. "
            "At 1.0 kg compare about 30.28 m here with 8.10 m at default gravity."
        ),
        ("Gravity is fixed at 3.71 m/s^2.", "This is not a complete planet model."),
    ),
)
