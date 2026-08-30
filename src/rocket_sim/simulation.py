"""Deterministic flight lifecycle and fixed-timestep simulation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from .config import SimulationConfig, Vector2
from .physics import (
    ForceBreakdown,
    acceleration_m_s2,
    drag_force_n,
    force_breakdown_n,
    gravity_force_n,
    semi_implicit_impulse_step,
    thrust_impulse_n_s,
)


class FlightPhase(str, Enum):
    READY = "ready"
    POWERED = "powered"
    COAST = "coast"
    LANDED = "landed"


@dataclass(frozen=True, slots=True)
class RocketState:
    time_s: float
    position_m: Vector2
    velocity_m_s: Vector2
    acceleration_m_s2: Vector2
    mass_kg: float
    phase: FlightPhase
    has_lifted_off: bool


class Simulation:
    """Own a single constant-mass rocket flight and its recorded trajectory."""

    def __init__(self, config: SimulationConfig | None = None) -> None:
        self._config = config or SimulationConfig()
        self._reset_run_state()

    @property
    def config(self) -> SimulationConfig:
        """Return the immutable configuration owned by this simulation run."""

        return self._config

    def _reset_run_state(self) -> None:
        self._state = self._initial_state()
        self._trajectory: list[RocketState] = [self._state]
        self._accumulator_s = 0.0
        self._accumulator_compensation_s = 0.0
        self._is_running = False
        self._physics_step_count = 0

    def replace_ready_config(self, config: SimulationConfig) -> bool:
        """Atomically replace setup and rebuild state only while READY."""

        if not isinstance(config, SimulationConfig):
            raise TypeError("config must be a SimulationConfig")
        if self._state.phase is not FlightPhase.READY:
            return False

        self._config = config
        self._reset_run_state()
        return True

    @property
    def state(self) -> RocketState:
        return self._state

    @property
    def trajectory(self) -> tuple[RocketState, ...]:
        return tuple(self._trajectory)

    @property
    def accumulator_s(self) -> float:
        return self._accumulator_s - self._accumulator_compensation_s

    @property
    def physics_step_count(self) -> int:
        return self._physics_step_count

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def is_finished(self) -> bool:
        return self._state.phase is FlightPhase.LANDED

    @property
    def is_paused(self) -> bool:
        return (
            not self._is_running
            and self._state.phase not in (FlightPhase.READY, FlightPhase.LANDED)
        )

    @property
    def current_thrust_n(self) -> float:
        return self.current_forces.thrust_n.magnitude

    @property
    def delivered_impulse_ns(self) -> float:
        return self.config.thrust_curve.delivered_impulse_ns(self._state.time_s)

    @property
    def current_forces(self) -> ForceBreakdown:
        """Return forces at the current state, inactive while still ready."""

        if self._state.phase is FlightPhase.READY:
            return ForceBreakdown.zero()
        return force_breakdown_n(
            self.config,
            self._state.time_s,
            self._state.velocity_m_s,
        )

    def _initial_state(self) -> RocketState:
        return RocketState(
            time_s=0.0,
            position_m=self.config.initial_position_m,
            velocity_m_s=self.config.initial_velocity_m_s,
            acceleration_m_s2=Vector2(0.0, 0.0),
            mass_kg=self.config.mass_kg,
            phase=FlightPhase.READY,
            has_lifted_off=self.config.initial_position_m.y > 0.0,
        )

    def launch(self) -> None:
        """Start a ready flight without accumulating pre-launch wall time."""

        if self._state.phase is not FlightPhase.READY:
            return

        initial_acceleration = acceleration_m_s2(
            self.config, 0.0, self._state.velocity_m_s
        )
        can_leave_ground = self._state.position_m.y > 0.0
        if self._state.position_m.y == 0.0 and self._state.velocity_m_s.y >= 0.0:
            first_segment_s = min(
                (
                    *self.config.thrust_curve.knots_strictly_between(
                        0.0, self.config.physics_dt_s
                    ),
                    self.config.physics_dt_s,
                )
            )
            initial_other_force = gravity_force_n(
                self.config.mass_kg, self.config.gravity_m_s2
            ) + drag_force_n(self.config, self._state.velocity_m_s)
            trial_position, _ = semi_implicit_impulse_step(
                self._state.position_m,
                self._state.velocity_m_s,
                thrust_impulse_n_s(self.config, 0.0, first_segment_s),
                initial_other_force,
                self.config.mass_kg,
                first_segment_s,
            )
            can_leave_ground = trial_position.y > 0.0
        if not can_leave_ground:
            self._state = RocketState(
                time_s=0.0,
                position_m=Vector2(self._state.position_m.x, 0.0),
                velocity_m_s=self._state.velocity_m_s,
                acceleration_m_s2=initial_acceleration,
                mass_kg=self.config.mass_kg,
                phase=FlightPhase.LANDED,
                has_lifted_off=False,
            )
            self._trajectory = [self._state]
            return

        self._state = RocketState(
            time_s=0.0,
            position_m=self._state.position_m,
            velocity_m_s=self._state.velocity_m_s,
            acceleration_m_s2=initial_acceleration,
            mass_kg=self.config.mass_kg,
            phase=self._phase_at(0.0),
            has_lifted_off=self._state.has_lifted_off,
        )
        self._trajectory[0] = self._state
        self._is_running = True

    def toggle_pause(self) -> None:
        """Launch when ready, otherwise pause or resume a live flight."""

        if self._state.phase is FlightPhase.READY:
            self.launch()
        elif self._state.phase is not FlightPhase.LANDED:
            self._is_running = not self._is_running

    def reset(self) -> None:
        """Restore run state while preserving the selected configuration."""

        self._reset_run_state()

    def advance_elapsed(self, elapsed_s: float) -> int:
        """Consume wall time through fixed physics steps and return their count."""

        if not math.isfinite(elapsed_s) or elapsed_s < 0.0:
            raise ValueError("elapsed_s must be finite and non-negative")
        if not self._is_running or self.is_finished:
            return 0

        self._add_accumulator(elapsed_s)
        steps = 0
        dt = self.config.physics_dt_s
        while self.accumulator_s >= dt and self._is_running:
            self._take_fixed_step()
            steps += 1
            self._add_accumulator(-dt)

        if self.is_finished:
            self._clear_accumulator()
        return steps

    def _add_accumulator(self, duration_s: float) -> None:
        corrected = duration_s - self._accumulator_compensation_s
        updated = self._accumulator_s + corrected
        self._accumulator_compensation_s = (
            updated - self._accumulator_s
        ) - corrected
        self._accumulator_s = updated

    def _clear_accumulator(self) -> None:
        self._accumulator_s = 0.0
        self._accumulator_compensation_s = 0.0

    def step(self) -> bool:
        """Advance exactly one configured physics step when running."""

        if not self._is_running or self.is_finished:
            return False
        self._take_fixed_step()
        return True

    def single_step_paused(self) -> bool:
        """Advance one production fixed step during a live paused flight."""

        if not self.is_paused:
            return False
        self._take_fixed_step()
        return True

    def _take_fixed_step(self) -> None:
        self._advance_fixed_step(self.config.physics_dt_s)
        self._physics_step_count += 1

    def _phase_at(self, time_s: float) -> FlightPhase:
        if 0.0 <= time_s < self.config.thrust_curve.burn_duration_s:
            return FlightPhase.POWERED
        return FlightPhase.COAST

    def _advance_fixed_step(self, duration_s: float) -> None:
        start_s = self._state.time_s
        target_s = start_s + duration_s
        boundaries = (
            *self.config.thrust_curve.knots_strictly_between(start_s, target_s),
            target_s,
        )
        for boundary_s in boundaries:
            self._advance_segment_to(boundary_s)
            if self.is_finished:
                break

    def _advance_segment_to(self, target_time_s: float) -> None:
        previous = self._state
        duration_s = target_time_s - previous.time_s
        other_force = gravity_force_n(
            self.config.mass_kg, self.config.gravity_m_s2
        ) + drag_force_n(self.config, previous.velocity_m_s)
        trial_position, trial_velocity = semi_implicit_impulse_step(
            previous.position_m,
            previous.velocity_m_s,
            thrust_impulse_n_s(self.config, previous.time_s, target_time_s),
            other_force,
            self.config.mass_kg,
            duration_s,
        )
        lifted_off = previous.has_lifted_off or trial_position.y > 0.0

        if (
            previous.has_lifted_off
            and previous.position_m.y > 0.0
            and trial_position.y <= 0.0
            and trial_velocity.y < 0.0
        ):
            alpha = previous.position_m.y / (
                previous.position_m.y - trial_position.y
            )
            impact_time_s = previous.time_s + alpha * duration_s
            impact_position = Vector2(
                previous.position_m.x
                + alpha * (trial_position.x - previous.position_m.x),
                0.0,
            )
            impact_velocity = previous.velocity_m_s + (
                trial_velocity - previous.velocity_m_s
            ) * alpha
            self._state = RocketState(
                time_s=impact_time_s,
                position_m=impact_position,
                velocity_m_s=impact_velocity,
                acceleration_m_s2=acceleration_m_s2(
                    self.config, impact_time_s, impact_velocity
                ),
                mass_kg=self.config.mass_kg,
                phase=FlightPhase.LANDED,
                has_lifted_off=True,
            )
            self._trajectory.append(self._state)
            self._is_running = False
            self._clear_accumulator()
            return

        if not previous.has_lifted_off and trial_position.y <= 0.0:
            self._state = RocketState(
                time_s=previous.time_s,
                position_m=Vector2(previous.position_m.x, 0.0),
                velocity_m_s=previous.velocity_m_s,
                acceleration_m_s2=acceleration_m_s2(
                    self.config, previous.time_s, previous.velocity_m_s
                ),
                mass_kg=self.config.mass_kg,
                phase=FlightPhase.LANDED,
                has_lifted_off=False,
            )
            self._trajectory.append(self._state)
            self._is_running = False
            self._clear_accumulator()
            return

        self._state = RocketState(
            time_s=target_time_s,
            position_m=trial_position,
            velocity_m_s=trial_velocity,
            acceleration_m_s2=acceleration_m_s2(
                self.config, target_time_s, trial_velocity
            ),
            mass_kg=self.config.mass_kg,
            phase=self._phase_at(target_time_s),
            has_lifted_off=lifted_off,
        )
        self._trajectory.append(self._state)
