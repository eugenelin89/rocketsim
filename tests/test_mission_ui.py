import os
from dataclasses import replace
import math
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from rocket_sim import Simulation, SimulationConfig, Vector2
from rocket_sim.app import dispatch_action, handle_mouse_button
from rocket_sim.game import GameSession, GameView
from rocket_sim.missions import FlightResult, MISSIONS
from rocket_sim.rendering import (
    ALTITUDE_TARGET_X_MAX_M,
    ALTITUDE_TARGET_X_MIN_M,
    Renderer,
    mission_hud_rows,
    mission_result_rows,
    mission_target_geometry,
    world_to_screen,
)
from rocket_sim.setup import AppAction, AppActionKind, SetupParameter


def _session_snapshot(game: GameSession) -> tuple[object, ...]:
    simulation = game.simulation
    return (
        game.view,
        game.current_mission_index,
        game.result,
        game.evaluation,
        dict(game.best),
        game.unlocked_count,
        game.countdown_remaining_s,
        simulation.config,
        id(simulation.config),
        simulation.state,
        simulation.trajectory,
        simulation.accumulator_s,
        simulation.physics_step_count,
        simulation.is_running,
        simulation.is_paused,
        simulation.is_finished,
    )


def test_mouse_routes_mode_select_mission_select_brief_and_configure() -> None:
    pygame.init()
    try:
        renderer = Renderer()
        game = GameSession()

        controls = {c.identifier: c for c in renderer._screen_controls(game)}
        assert handle_mouse_button(
            1, controls["missions"].rect.center, game.simulation, renderer, game
        )
        assert game.view is GameView.MISSION_SELECT

        controls = {c.identifier: c for c in renderer._screen_controls(game)}
        assert handle_mouse_button(
            1, controls["mission.0"].rect.center, game.simulation, renderer, game
        )
        assert game.view is GameView.MISSION_BRIEF

        controls = {c.identifier: c for c in renderer._screen_controls(game)}
        assert handle_mouse_button(
            1, controls["begin_mission"].rect.center, game.simulation, renderer, game
        )
        assert game.view is GameView.MISSION_FLIGHT
        assert game.simulation.config is MISSIONS[0].base_config
    finally:
        pygame.quit()


def test_locked_mission_is_visible_but_not_clickable() -> None:
    pygame.init()
    try:
        renderer = Renderer()
        game = GameSession()
        game.open_missions()
        locked = next(
            control
            for control in renderer._screen_controls(game)
            if control.identifier == "mission.1"
        )

        assert not locked.enabled
        assert renderer.action_at(locked.rect.center, game.simulation, game) is None
        assert game.current_mission is None
    finally:
        pygame.quit()


def test_direct_disallowed_action_and_global_defaults_cannot_bypass_mission() -> None:
    game = GameSession(unlock_all=True)
    game.open_missions()
    game.select_mission(1)
    game.begin_mission()
    before = game.simulation.config

    dispatch_action(
        AppAction(
            AppActionKind.ADJUST_SETUP,
            SetupParameter.GRAVITY,
            -1,
        ),
        game.simulation,
        game=game,
    )
    assert game.simulation.config == before

    dispatch_action(
        AppAction(AppActionKind.RESTORE_DEFAULTS),
        game.simulation,
        game=game,
    )
    assert game.simulation.config is MISSIONS[1].base_config
    assert game.simulation.config.thrust_curve is before.thrust_curve
    assert game.simulation.config.physics_dt_s == before.physics_dt_s


def test_mission_setup_hitboxes_enable_only_allowed_field() -> None:
    pygame.init()
    try:
        renderer = Renderer()
        game = GameSession(unlock_all=True)
        game.open_missions()
        game.select_mission(3)
        game.begin_mission()
        controls = renderer.setup_controls(
            game.simulation, game.current_mission.allowed_setup_fields
        )

        for control in controls:
            if ".decrease" in control.identifier or ".increase" in control.identifier:
                expected = control.identifier.startswith("drag_coefficient.")
                assert control.enabled is expected
                assert (
                    renderer.action_at(control.rect.center, game.simulation, game)
                    == control.action
                ) is expected
    finally:
        pygame.quit()


def test_target_geometry_uses_shared_world_transform_with_mission_coordinates() -> None:
    mission = MISSIONS[1]
    objective = mission.objectives[0]
    origin = (400.0, 650.0)
    scale = 20.0

    with patch(
        "rocket_sim.rendering.world_to_screen", wraps=world_to_screen
    ) as transform:
        geometry = mission_target_geometry(mission, origin, scale)

    assert [call.args[0] for call in transform.call_args_list] == [
        Vector2(objective.lower, 0.0),
        Vector2(objective.upper, 0.0),
    ]
    assert geometry.start_px == world_to_screen(
        Vector2(objective.lower, 0.0), origin, scale
    )
    assert geometry.end_px == world_to_screen(
        Vector2(objective.upper, 0.0), origin, scale
    )


def test_apogee_band_geometry_transforms_both_world_altitude_bounds() -> None:
    mission = MISSIONS[4]
    objective = mission.objectives[0]
    origin = (400.0, 650.0)
    scale = 20.0

    with patch(
        "rocket_sim.rendering.world_to_screen", wraps=world_to_screen
    ) as transform:
        geometry = mission_target_geometry(mission, origin, scale)

    assert {call.args[0] for call in transform.call_args_list} == {
        Vector2(ALTITUDE_TARGET_X_MIN_M, objective.lower),
        Vector2(ALTITUDE_TARGET_X_MAX_M, objective.lower),
        Vector2(ALTITUDE_TARGET_X_MIN_M, objective.upper),
        Vector2(ALTITUDE_TARGET_X_MAX_M, objective.upper),
    }
    assert geometry.start_px == world_to_screen(
        Vector2(ALTITUDE_TARGET_X_MIN_M, objective.lower), origin, scale
    )
    assert geometry.end_px == world_to_screen(
        Vector2(ALTITUDE_TARGET_X_MAX_M, objective.lower), origin, scale
    )
    assert geometry.secondary_start_px == world_to_screen(
        Vector2(ALTITUDE_TARGET_X_MIN_M, objective.upper), origin, scale
    )
    assert geometry.secondary_end_px == world_to_screen(
        Vector2(ALTITUDE_TARGET_X_MAX_M, objective.upper), origin, scale
    )


def test_landing_hud_stays_pending_even_when_current_x_is_inside_zone() -> None:
    mission = MISSIONS[1]
    simulation = Simulation(
        replace(
            mission.base_config,
            initial_position_m=Vector2(18.1, 1.0),
            initial_velocity_m_s=Vector2(0.0, 1.0),
        )
    )

    rows = mission_hud_rows(mission, simulation)

    assert rows[-1].startswith("[...]")


def test_result_rows_are_sourced_from_evaluation_and_physical_result() -> None:
    mission = MISSIONS[1]
    simulation = Simulation(
        replace(
            mission.base_config, launch_angle_rad=math.radians(60.0)
        )
    )
    simulation.launch()
    while not simulation.is_finished:
        simulation.step()
    result = FlightResult.from_simulation(simulation)
    evaluation = mission.evaluate(result)

    text = "\n".join(mission_result_rows(mission, evaluation, result))

    assert str(evaluation.score) in text
    assert f"{result.apogee_m:.3f}" in text
    assert f"{result.landing_x_m:.3f}" in text
    assert f"{result.impact_speed_m_s:.3f}" in text
    assert evaluation.objectives[0].feedback in text
    assert "PHYSICS EXPLANATION" in text
    assert mission.hint in text


def test_every_game_view_renders_without_mutating_session_or_simulation() -> None:
    pygame.init()
    try:
        surface = pygame.Surface((1200, 720))
        renderer = Renderer()
        game = GameSession(unlock_all=True)

        for view_setup in ("mode", "select", "brief", "flight"):
            if view_setup == "select":
                game.open_missions()
            elif view_setup == "brief":
                game.open_missions()
                game.select_mission(0)
            elif view_setup == "flight":
                game.begin_mission()
            before = _session_snapshot(game)
            renderer.draw(surface, game.simulation, game)
            assert _session_snapshot(game) == before

        game.adjust_setup(SetupParameter.MASS, -1)
        game.primary()
        game.advance_elapsed(20.0)
        assert game.view is GameView.MISSION_RESULTS
        before = _session_snapshot(game)
        renderer.draw(surface, game.simulation, game)
        renderer.draw(surface, game.simulation, game)
        assert _session_snapshot(game) == before
    finally:
        pygame.quit()


def test_results_buttons_offer_retry_missions_sandbox_and_only_valid_next() -> None:
    pygame.init()
    try:
        renderer = Renderer()
        game = GameSession()
        game.open_missions()
        game.select_mission(0)
        game.begin_mission()
        game.primary()
        game.advance_elapsed(20.0)
        controls = {c.identifier: c for c in renderer._screen_controls(game)}

        assert controls["retry"].enabled
        assert controls["results_missions"].enabled
        assert controls["results_sandbox"].enabled
        assert not controls["next"].enabled
    finally:
        pygame.quit()


def test_result_navigation_buttons_dispatch_retry_missions_and_sandbox() -> None:
    pygame.init()
    try:
        renderer = Renderer()
        game = GameSession()
        game.open_missions()
        game.select_mission(0)
        game.begin_mission()
        selected = game.simulation.config
        game.primary()
        game.advance_elapsed(20.0)
        retry = {c.identifier: c for c in renderer._screen_controls(game)}["retry"]
        handle_mouse_button(1, retry.rect.center, game.simulation, renderer, game)
        assert game.view is GameView.MISSION_FLIGHT
        assert game.simulation.config is selected
        assert game.simulation.state.phase.value == "ready"

        game.primary()
        game.advance_elapsed(20.0)
        missions = {c.identifier: c for c in renderer._screen_controls(game)}[
            "results_missions"
        ]
        handle_mouse_button(1, missions.rect.center, game.simulation, renderer, game)
        assert game.view is GameView.MISSION_SELECT

        game.select_mission(0)
        game.begin_mission()
        game.primary()
        game.advance_elapsed(20.0)
        sandbox = {c.identifier: c for c in renderer._screen_controls(game)}[
            "results_sandbox"
        ]
        handle_mouse_button(1, sandbox.rect.center, game.simulation, renderer, game)
        assert game.view is GameView.SANDBOX
        assert game.current_mission is None
        assert game.simulation.config == SimulationConfig()
    finally:
        pygame.quit()


def test_success_result_next_button_dispatches_to_unlocked_brief() -> None:
    pygame.init()
    try:
        renderer = Renderer()
        game = GameSession()
        game.open_missions()
        game.select_mission(0)
        game.begin_mission()
        game.adjust_setup(SetupParameter.MASS, -1)
        game.primary()
        game.advance_elapsed(20.0)
        next_control = {c.identifier: c for c in renderer._screen_controls(game)}[
            "next"
        ]

        assert next_control.enabled
        handle_mouse_button(
            1, next_control.rect.center, game.simulation, renderer, game
        )
        assert game.view is GameView.MISSION_BRIEF
        assert game.current_mission_index == 1
        assert game.simulation.config is MISSIONS[1].base_config
    finally:
        pygame.quit()
