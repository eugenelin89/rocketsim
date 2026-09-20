"""Pygame-independent Mission Mode session state above ``Simulation``."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from .missions import FlightResult, MISSIONS, Mission, MissionEvaluation
from .setup import SetupParameter, adjusted_setup_config
from .simulation import FlightPhase, Simulation


class GameView(str, Enum):
    MODE_SELECT = "mode_select"
    SANDBOX = "sandbox"
    MISSION_SELECT = "mission_select"
    MISSION_BRIEF = "mission_brief"
    MISSION_FLIGHT = "mission_flight"
    MISSION_RESULTS = "mission_results"


@dataclass(frozen=True, slots=True)
class MissionBest:
    score: int
    stars: int


class GameSession:
    """Own app navigation and evaluation while delegating physics unchanged."""

    def __init__(
        self,
        missions: tuple[Mission, ...] = MISSIONS,
        *,
        unlock_all: bool = False,
    ) -> None:
        if not missions:
            raise ValueError("at least one mission is required")
        self.missions = missions
        self.view = GameView.MODE_SELECT
        self.simulation = Simulation()
        self.current_mission_index: int | None = None
        self.result: FlightResult | None = None
        self.evaluation: MissionEvaluation | None = None
        self.best: dict[str, MissionBest] = {}
        self.unlocked_count = len(missions) if unlock_all else 1
        self.countdown_remaining_s: float | None = None

    @property
    def current_mission(self) -> Mission | None:
        if self.current_mission_index is None:
            return None
        return self.missions[self.current_mission_index]

    def open_sandbox(self) -> None:
        self.view = GameView.SANDBOX
        self.simulation = Simulation()
        self.current_mission_index = None
        self.result = None
        self.evaluation = None
        self.countdown_remaining_s = None

    def open_missions(self) -> None:
        self.view = GameView.MISSION_SELECT
        self.current_mission_index = None
        self.result = None
        self.evaluation = None
        self.countdown_remaining_s = None

    def select_mission(self, index: int) -> bool:
        if self.view not in {GameView.MISSION_SELECT, GameView.MISSION_RESULTS}:
            return False
        if not 0 <= index < len(self.missions) or index >= self.unlocked_count:
            return False
        self.current_mission_index = index
        self.simulation = Simulation(self.missions[index].base_config)
        self.result = None
        self.evaluation = None
        self.countdown_remaining_s = None
        self.view = GameView.MISSION_BRIEF
        return True

    def begin_mission(self) -> bool:
        if self.view is not GameView.MISSION_BRIEF or self.current_mission is None:
            return False
        self.view = GameView.MISSION_FLIGHT
        return True

    def setup_allowed(self, parameter: SetupParameter) -> bool:
        mission = self.current_mission
        return (
            self.view is GameView.MISSION_FLIGHT
            and mission is not None
            and parameter in mission.allowed_setup_fields
        )

    def adjust_setup(self, parameter: SetupParameter, direction: int) -> bool:
        if not self.setup_allowed(parameter):
            return False
        replacement = adjusted_setup_config(
            self.simulation.config, parameter, direction
        )
        return self.simulation.replace_ready_config(replacement)

    def restore_mission_defaults(self) -> bool:
        mission = self.current_mission
        if (
            self.view is not GameView.MISSION_FLIGHT
            or mission is None
            or self.simulation.state.phase is not FlightPhase.READY
        ):
            return False
        return self.simulation.replace_ready_config(mission.base_config)

    def primary(self) -> None:
        if self.view is GameView.SANDBOX:
            self.simulation.toggle_pause()
        elif self.view is GameView.MISSION_FLIGHT:
            if self.simulation.state.phase is FlightPhase.READY:
                if self.countdown_remaining_s is None:
                    self.countdown_remaining_s = 3.0
            elif not self.simulation.is_finished:
                self.simulation.toggle_pause()

    def advance_elapsed(self, elapsed_s: float) -> int:
        """Advance presentation countdown, then the unmodified simulation."""

        if not math.isfinite(elapsed_s) or elapsed_s < 0.0:
            return self.simulation.advance_elapsed(elapsed_s)
        if self.view is GameView.SANDBOX:
            return self.simulation.advance_elapsed(elapsed_s)
        if self.view is not GameView.MISSION_FLIGHT:
            return 0

        remaining = elapsed_s
        if self.countdown_remaining_s is not None:
            if math.isclose(
                remaining,
                self.countdown_remaining_s,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                remaining = self.countdown_remaining_s
            consumed = min(remaining, self.countdown_remaining_s)
            self.countdown_remaining_s -= consumed
            remaining -= consumed
            if self.countdown_remaining_s > 0.0:
                return 0
            self.countdown_remaining_s = None
            self.simulation.launch()

        steps = self.simulation.advance_elapsed(remaining)
        self._finalize_if_terminal()
        return steps

    def _finalize_if_terminal(self) -> None:
        if not self.simulation.is_finished or self.result is not None:
            return
        mission = self.current_mission
        if mission is None:
            return
        self.result = FlightResult.from_simulation(self.simulation)
        self.evaluation = mission.evaluate(self.result)
        prior = self.best.get(mission.id)
        if prior is None or self.evaluation.score > prior.score:
            self.best[mission.id] = MissionBest(
                self.evaluation.score, self.evaluation.stars
            )
        if self.evaluation.success and self.current_mission_index is not None:
            self.unlocked_count = min(
                len(self.missions),
                max(self.unlocked_count, self.current_mission_index + 2),
            )
        self.view = GameView.MISSION_RESULTS

    def retry(self) -> bool:
        if self.view is not GameView.MISSION_RESULTS:
            return False
        self.simulation.reset()
        self.result = None
        self.evaluation = None
        self.countdown_remaining_s = None
        self.view = GameView.MISSION_FLIGHT
        return True

    def reset_mission(self) -> bool:
        mission = self.current_mission
        if mission is None or self.view not in {
            GameView.MISSION_FLIGHT,
            GameView.MISSION_RESULTS,
        }:
            return False
        self.simulation = Simulation(mission.base_config)
        self.result = None
        self.evaluation = None
        self.countdown_remaining_s = None
        self.view = GameView.MISSION_FLIGHT
        return True

    def next_mission(self) -> bool:
        if (
            self.view is not GameView.MISSION_RESULTS
            or self.evaluation is None
            or not self.evaluation.success
            or self.current_mission_index is None
        ):
            return False
        next_index = self.current_mission_index + 1
        if next_index >= len(self.missions):
            return False
        return self.select_mission(next_index)
