from dataclasses import replace
import math

import pytest

from rocket_sim import Simulation, SimulationConfig
from rocket_sim.game import GameSession, GameView
from rocket_sim.missions import (
    FlightOutcome,
    FlightResult,
    MISSIONS,
    ObjectiveKind,
    stars_for_score,
)
from rocket_sim.setup import SetupParameter


def _run(config: SimulationConfig) -> Simulation:
    simulation = Simulation(config)
    simulation.launch()
    while not simulation.is_finished:
        assert simulation.step()
    return simulation


def _result(
    *,
    apogee_m: float = 10.0,
    landing_x_m: float | None = 18.1,
    mass_kg: float = 1.0,
    outcome: FlightOutcome = FlightOutcome.LANDED,
) -> FlightResult:
    lifted = outcome is FlightOutcome.LANDED
    return FlightResult(
        outcome=outcome,
        config=SimulationConfig(mass_kg=mass_kg),
        apogee_m=apogee_m,
        landing_x_m=landing_x_m if lifted else None,
        impact_speed_m_s=12.0 if lifted else None,
        max_speed_m_s=14.0 if lifted else 0.0,
        max_acceleration_m_s2=18.0 if lifted else 0.0,
        max_drag_n=2.0 if lifted else 0.0,
        flight_time_s=3.0 if lifted else 0.0,
        liftoff_occurred=lifted,
    )


def _snapshot(simulation: Simulation) -> tuple[object, ...]:
    return (
        simulation.config,
        id(simulation.config),
        simulation.state,
        simulation.trajectory,
        simulation.accumulator_s,
        simulation.physics_step_count,
        simulation.is_running,
        simulation.is_paused,
        simulation.is_finished,
        simulation.current_forces,
        simulation.delivered_impulse_ns,
    )


def test_flight_result_requires_a_terminal_production_run() -> None:
    ready = Simulation()
    with pytest.raises(ValueError, match="terminal"):
        FlightResult.from_simulation(ready)

    ready.launch()
    ready.step()
    with pytest.raises(ValueError, match="terminal"):
        FlightResult.from_simulation(ready)

    ready.toggle_pause()
    with pytest.raises(ValueError, match="terminal"):
        FlightResult.from_simulation(ready)


def test_flight_result_metrics_match_recorded_production_history_without_mutation() -> None:
    config = replace(
        SimulationConfig(), launch_angle_rad=math.radians(60.0)
    )
    simulation = _run(config)
    before = _snapshot(simulation)

    result = FlightResult.from_simulation(simulation)

    assert result.outcome is FlightOutcome.LANDED
    assert result.config is config
    assert result.configured_mass_kg == config.mass_kg
    assert result.apogee_m == max(s.position_m.y for s in simulation.trajectory)
    assert result.landing_x_m == simulation.state.position_m.x
    assert result.impact_speed_m_s == simulation.state.velocity_m_s.magnitude
    assert result.max_speed_m_s == max(
        s.velocity_m_s.magnitude for s in simulation.trajectory
    )
    assert result.max_acceleration_m_s2 == max(
        s.acceleration_m_s2.magnitude for s in simulation.trajectory
    )
    independent_drag = max(
        0.5
        * config.air_density_kg_m3
        * config.drag_coefficient
        * config.reference_area_m2
        * s.velocity_m_s.magnitude**2
        for s in simulation.trajectory
    )
    assert result.max_drag_n == pytest.approx(independent_drag, abs=1e-12)
    assert result.flight_time_s == simulation.state.time_s
    assert _snapshot(simulation) == before


def test_no_liftoff_has_no_fabricated_contact_or_impact_metrics() -> None:
    simulation = _run(replace(SimulationConfig(), mass_kg=2.0))
    result = FlightResult.from_simulation(simulation)

    assert result.outcome is FlightOutcome.NO_LIFTOFF
    assert not result.liftoff_occurred
    assert result.landing_x_m is None
    assert result.impact_speed_m_s is None
    assert result.flight_time_s == 0.0
    assert all(not objective.evaluate(result).passed for mission in MISSIONS for objective in mission.objectives)


@pytest.mark.parametrize("mission_index", range(5))
def test_objective_boundaries_are_inclusive_and_nextafter_exact(
    mission_index: int,
) -> None:
    objective = MISSIONS[mission_index].objectives[0]
    if objective.kind is ObjectiveKind.MINIMUM_APOGEE:
        assert objective.evaluate(_result(apogee_m=objective.lower)).passed
        assert not objective.evaluate(
            _result(apogee_m=math.nextafter(objective.lower, -math.inf))
        ).passed
    elif objective.kind is ObjectiveKind.APOGEE_BAND:
        assert objective.evaluate(_result(apogee_m=objective.lower)).passed
        assert objective.evaluate(_result(apogee_m=objective.upper)).passed
        assert not objective.evaluate(
            _result(apogee_m=math.nextafter(objective.lower, -math.inf))
        ).passed
        assert not objective.evaluate(
            _result(apogee_m=math.nextafter(objective.upper, math.inf))
        ).passed
    else:
        assert objective.evaluate(_result(landing_x_m=objective.lower)).passed
        assert objective.evaluate(_result(landing_x_m=objective.upper)).passed
        assert not objective.evaluate(
            _result(landing_x_m=math.nextafter(objective.lower, -math.inf))
        ).passed
        assert not objective.evaluate(
            _result(landing_x_m=math.nextafter(objective.upper, math.inf))
        ).passed


def test_scoring_and_star_thresholds_are_deterministic_and_explainable() -> None:
    mission = MISSIONS[0]
    one_star = mission.evaluate(_result(apogee_m=8.0))
    two_stars = mission.evaluate(_result(apogee_m=10.0))
    three_stars = mission.evaluate(_result(apogee_m=11.2))
    failure = mission.evaluate(_result(apogee_m=7.999))

    assert (one_star.score, one_star.stars) == (500, 1)
    assert (two_stars.score, two_stars.stars) == (750, 2)
    assert (three_stars.score, three_stars.stars) == (900, 3)
    assert (failure.score, failure.stars, failure.success) == (0, 0, False)
    for evaluation in (one_star, two_stars, three_stars, failure):
        assert evaluation.score == sum(c.points for c in evaluation.components)
        assert mission.evaluate(
            _result(apogee_m={1: 8.0, 2: 10.0, 3: 11.2, 0: 7.999}[evaluation.stars])
        ) == evaluation


@pytest.mark.parametrize(
    ("score", "stars"),
    ((0, 0), (499, 0), (500, 1), (749, 1), (750, 2), (899, 2), (900, 3)),
)
def test_star_boundaries_use_exact_integer_score_thresholds(
    score: int, stars: int
) -> None:
    assert stars_for_score(score) == stars


@pytest.mark.parametrize(
    ("mission_index", "values", "expected"),
    (
        (0, (("apogee_m", 5.0), ("apogee_m", 8.0), ("apogee_m", 10.0), ("apogee_m", 12.0), ("apogee_m", 15.0)), (0, 0, 250, 500, 500)),
        (2, (("mass_kg", 0.5), ("mass_kg", 1.0), ("mass_kg", 1.15), ("mass_kg", 1.3), ("mass_kg", 2.0)), (0, 0, 250, 500, 500)),
        (1, (("landing_x_m", 17.0), ("landing_x_m", 17.5), ("landing_x_m", 17.8), ("landing_x_m", 18.1), ("landing_x_m", 18.7)), (0, 0, 250, 500, 0)),
        (4, (("apogee_m", 19.0), ("apogee_m", 20.0), ("apogee_m", 20.75), ("apogee_m", 21.5), ("apogee_m", 23.0)), (0, 0, 250, 500, 0)),
    ),
)
def test_each_score_metric_has_independent_center_edge_and_clamp_evidence(
    mission_index: int,
    values: tuple[tuple[str, float], ...],
    expected: tuple[int, ...],
) -> None:
    rule = MISSIONS[mission_index].score_rule
    actual = []
    for field, value in values:
        kwargs = {field: value}
        if field == "mass_kg":
            result = _result(mass_kg=value)
        else:
            result = _result(**kwargs)
        actual.append(rule.points(result))
    assert tuple(actual) == expected


def test_contact_accuracy_missing_value_earns_no_performance_points() -> None:
    rule = MISSIONS[1].score_rule
    assert rule.points(_result(outcome=FlightOutcome.NO_LIFTOFF)) == 0


def test_heavy_lift_scoring_uses_result_config_not_a_separate_current_config() -> None:
    mission = MISSIONS[2]
    captured = _result(apogee_m=3.5, mass_kg=1.3)

    evaluation = mission.evaluate(captured)

    assert evaluation.success
    assert evaluation.score == 1000
    assert captured.configured_mass_kg == 1.3


@pytest.mark.parametrize(
    ("mission_index", "success_value", "failure_value", "parameter"),
    (
        (0, 1.0, 1.1, SetupParameter.MASS),
        (1, math.radians(60.0), math.radians(55.0), SetupParameter.LAUNCH_ANGLE),
        (2, 1.3, 1.4, SetupParameter.MASS),
        (3, 0.75, 1.0, SetupParameter.DRAG_COEFFICIENT),
        (4, 1.2, 1.0, SetupParameter.MASS),
    ),
)
def test_every_shipped_mission_is_achievable_and_failable_in_production(
    mission_index: int,
    success_value: float,
    failure_value: float,
    parameter: SetupParameter,
) -> None:
    mission = MISSIONS[mission_index]
    success_config = replace(
        mission.base_config, **{parameter.value: success_value}
    )
    failure_config = replace(
        mission.base_config, **{parameter.value: failure_value}
    )

    success = mission.evaluate(FlightResult.from_simulation(_run(success_config)))
    failure = mission.evaluate(FlightResult.from_simulation(_run(failure_config)))

    assert success.success
    assert not failure.success
    assert mission.base_config.gravity_m_s2 > 0.0
    assert parameter in mission.allowed_setup_fields


def test_mission_session_filters_all_setup_fields_and_preserves_fixed_values() -> None:
    session = GameSession(unlock_all=True)
    session.open_missions()
    assert session.select_mission(1)
    assert session.begin_mission()
    before = session.simulation.config

    for parameter in SetupParameter:
        accepted = session.adjust_setup(parameter, 1)
        if parameter is SetupParameter.LAUNCH_ANGLE:
            assert accepted
            assert session.simulation.config.launch_angle_rad != before.launch_angle_rad
            session.restore_mission_defaults()
        else:
            assert not accepted
            assert session.simulation.config == before

    after = session.simulation.config
    assert after.thrust_curve is before.thrust_curve
    assert after.physics_dt_s == before.physics_dt_s
    assert after.initial_position_m == before.initial_position_m
    assert after.initial_velocity_m_s == before.initial_velocity_m_s


def test_retry_preserves_selection_and_mission_reset_restores_exact_base() -> None:
    session = GameSession(unlock_all=True)
    session.open_missions()
    session.select_mission(0)
    session.begin_mission()
    assert session.adjust_setup(SetupParameter.MASS, -1)
    selected = session.simulation.config
    session.primary()
    session.advance_elapsed(20.0)
    assert session.view is GameView.MISSION_RESULTS

    assert session.retry()
    assert session.simulation.config is selected
    assert session.simulation.state.phase.value == "ready"
    assert session.result is None
    assert session.reset_mission()
    assert session.simulation.config is MISSIONS[0].base_config


def test_countdown_does_not_advance_physics_and_mission_matches_sandbox_after_ignition() -> None:
    session = GameSession(unlock_all=True)
    session.open_missions()
    session.select_mission(1)
    session.begin_mission()
    config = session.simulation.config
    before = _snapshot(session.simulation)
    session.primary()

    assert session.advance_elapsed(2.9) == 0
    assert _snapshot(session.simulation) == before
    assert session.advance_elapsed(0.1) == 0
    assert session.simulation.is_running

    sandbox = Simulation(config)
    sandbox.launch()
    for elapsed_s in (0.016, 0.017, 0.011, 0.25, 0.333):
        session.advance_elapsed(elapsed_s)
        sandbox.advance_elapsed(elapsed_s)

    assert session.simulation.config == sandbox.config
    assert session.simulation.state == sandbox.state
    assert session.simulation.trajectory == sandbox.trajectory
    assert session.simulation.physics_step_count == sandbox.physics_step_count
    assert session.simulation.accumulator_s == pytest.approx(sandbox.accumulator_s)
    assert session.simulation.current_forces == sandbox.current_forces
    assert session.simulation.delivered_impulse_ns == sandbox.delivered_impulse_ns

    while not session.simulation.is_finished:
        session.advance_elapsed(1.0 / 60.0)
        sandbox.advance_elapsed(1.0 / 60.0)

    assert session.simulation.state == sandbox.state
    assert session.simulation.trajectory == sandbox.trajectory
    assert session.simulation.physics_step_count == sandbox.physics_step_count
    assert session.simulation.accumulator_s == sandbox.accumulator_s == 0.0
    assert session.result == FlightResult.from_simulation(sandbox)


def test_countdown_boundary_remainder_advances_only_post_ignition_time() -> None:
    session = GameSession(unlock_all=True)
    session.open_missions()
    session.select_mission(1)
    session.begin_mission()
    session.primary()

    assert session.advance_elapsed(3.025) == 2
    assert session.simulation.state.time_s == pytest.approx(0.02, abs=1e-12)
    assert session.simulation.accumulator_s == pytest.approx(0.005, abs=1e-12)


@pytest.mark.parametrize("invalid", (math.nan, math.inf, -math.inf, -0.1))
def test_invalid_elapsed_time_is_atomic_during_countdown(invalid: float) -> None:
    session = GameSession(unlock_all=True)
    session.open_missions()
    session.select_mission(0)
    session.begin_mission()
    session.primary()
    before = _snapshot(session.simulation), session.countdown_remaining_s

    with pytest.raises(ValueError, match="finite and non-negative"):
        session.advance_elapsed(invalid)

    assert (_snapshot(session.simulation), session.countdown_remaining_s) == before


def test_no_liftoff_mission_path_matches_raw_simulation_exactly() -> None:
    mission = replace(
        MISSIONS[0],
        base_config=replace(MISSIONS[0].base_config, mass_kg=2.0),
    )
    session = GameSession((mission,), unlock_all=True)
    session.open_missions()
    session.select_mission(0)
    session.begin_mission()
    session.primary()
    session.advance_elapsed(3.0)

    sandbox = Simulation(mission.base_config)
    sandbox.launch()

    assert session.simulation.state == sandbox.state
    assert session.simulation.trajectory == sandbox.trajectory
    assert session.simulation.physics_step_count == sandbox.physics_step_count
    assert session.result == FlightResult.from_simulation(sandbox)
    assert session.result.outcome is FlightOutcome.NO_LIFTOFF


def test_progression_finalizes_once_keeps_best_and_unlocks_only_on_success() -> None:
    session = GameSession()
    session.open_missions()
    session.select_mission(0)
    session.begin_mission()
    session.adjust_setup(SetupParameter.MASS, -1)
    session.primary()
    session.advance_elapsed(20.0)

    assert session.view is GameView.MISSION_RESULTS
    assert session.evaluation is not None and session.evaluation.success
    assert session.unlocked_count == 2
    best = dict(session.best)
    session.advance_elapsed(20.0)
    assert session.best == best
    assert session.next_mission()
    assert session.current_mission_index == 1
    assert session.view is GameView.MISSION_BRIEF


def test_failed_mission_does_not_unlock_next_or_offer_next_transition() -> None:
    session = GameSession()
    session.open_missions()
    session.select_mission(0)
    session.begin_mission()
    session.primary()
    session.advance_elapsed(20.0)

    assert session.evaluation is not None and not session.evaluation.success
    assert session.unlocked_count == 1
    assert not session.next_mission()
