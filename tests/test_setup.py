import os
from dataclasses import fields, replace
import math
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from rocket_sim import (
    FlightPhase,
    Simulation,
    SimulationConfig,
    ThrustCurve,
    ThrustSample,
    Vector2,
)
from rocket_sim.app import dispatch_action, handle_event
from rocket_sim.rendering import (
    Renderer,
    launch_direction_preview_endpoint,
    setup_read_only_rows,
)
from rocket_sim.setup import (
    AppAction,
    AppActionKind,
    SETUP_PARAMETER_SPECS,
    SetupParameter,
    adjusted_setup_config,
    setup_display_rows,
    setup_display_value,
)


def _custom_curve() -> ThrustCurve:
    return ThrustCurve(
        (ThrustSample(0.0, 10.0), ThrustSample(1.0, 10.0))
    )


def _midrange_config(curve: ThrustCurve | None = None) -> SimulationConfig:
    return SimulationConfig(
        mass_kg=1.0,
        thrust_curve=curve or _custom_curve(),
        launch_angle_rad=math.radians(50.0),
        gravity_m_s2=9.81,
        air_density_kg_m3=1.225,
        drag_coefficient=0.75,
        reference_area_m2=0.010,
        physics_dt_s=0.037,
        initial_position_m=Vector2(0.0, 1.0),
        initial_velocity_m_s=Vector2(0.25, -0.5),
    )


def _simulation_snapshot(simulation: Simulation) -> tuple[object, ...]:
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
    )


def _control(renderer: Renderer, simulation: Simulation, identifier: str):
    return next(
        control
        for control in renderer.setup_controls(simulation)
        if control.identifier == identifier
    )


def _config_with_display_value(
    parameter: SetupParameter, value: float
) -> SimulationConfig:
    physical_value = (
        math.radians(value)
        if parameter is SetupParameter.LAUNCH_ANGLE
        else value
    )
    return replace(SimulationConfig(), **{parameter.value: physical_value})


def test_gui_specs_and_defaults_match_production_configuration_exactly() -> None:
    config = SimulationConfig()
    simulation = Simulation()
    expected_specs = (
        (SetupParameter.MASS, 0.1, 10.0, 0.1, 2),
        (SetupParameter.LAUNCH_ANGLE, 10.0, 90.0, 5.0, 0),
        (SetupParameter.DRAG_COEFFICIENT, 0.0, 2.0, 0.05, 2),
        (SetupParameter.REFERENCE_AREA, 0.001, 0.100, 0.001, 3),
        (SetupParameter.AIR_DENSITY, 0.0, 2.0, 0.05, 3),
        (SetupParameter.GRAVITY, 0.0, 20.0, 0.25, 2),
    )
    expected_labels = (
        (SetupParameter.MASS, "ROCKET", "Mass (constant/run)", "kg"),
        (
            SetupParameter.LAUNCH_ANGLE,
            "LAUNCH",
            "Fixed thrust direction",
            "deg",
        ),
        (
            SetupParameter.DRAG_COEFFICIENT,
            "AERODYNAMICS",
            "Drag coefficient Cd",
            "",
        ),
        (
            SetupParameter.REFERENCE_AREA,
            "AERODYNAMICS",
            "Reference area",
            "m^2",
        ),
        (
            SetupParameter.AIR_DENSITY,
            "ENVIRONMENT",
            "Air density",
            "kg/m^3",
        ),
        (
            SetupParameter.GRAVITY,
            "ENVIRONMENT",
            "Gravity",
            "m/s^2",
        ),
    )

    assert simulation.config == config
    assert tuple(
        (
            spec.parameter,
            spec.minimum,
            spec.maximum,
            spec.step,
            spec.decimal_places,
        )
        for spec in SETUP_PARAMETER_SPECS
    ) == expected_specs
    assert tuple(
        (spec.parameter, spec.group, spec.label, spec.unit)
        for spec in SETUP_PARAMETER_SPECS
    ) == expected_labels
    assert {
        row.parameter: row.value for row in setup_display_rows(config)
    } == {
        SetupParameter.MASS: "1.00 kg",
        SetupParameter.LAUNCH_ANGLE: "90 deg",
        SetupParameter.DRAG_COEFFICIENT: "0.75",
        SetupParameter.REFERENCE_AREA: "0.010 m^2",
        SetupParameter.AIR_DENSITY: "1.225 kg/m^3",
        SetupParameter.GRAVITY: "9.81 m/s^2",
    }
    assert setup_read_only_rows(config) == (
        "MOTOR (read-only): current sampled curve",
        "Total impulse 17.580 N*s   Physics dt: 0.010 s",
    )


def test_ready_config_replacement_atomically_rebuilds_complete_state() -> None:
    simulation = Simulation()
    curve = _custom_curve()
    replacement = SimulationConfig(
        mass_kg=3.25,
        thrust_curve=curve,
        launch_angle_rad=math.radians(35.0),
        gravity_m_s2=4.5,
        air_density_kg_m3=0.8,
        drag_coefficient=1.1,
        reference_area_m2=0.023,
        physics_dt_s=0.037,
        initial_position_m=Vector2(2.0, 4.0),
        initial_velocity_m_s=Vector2(-1.0, 3.0),
    )

    assert simulation.replace_ready_config(replacement)
    assert simulation.config is replacement
    assert simulation.state.time_s == 0.0
    assert simulation.state.position_m == replacement.initial_position_m
    assert simulation.state.velocity_m_s == replacement.initial_velocity_m_s
    assert simulation.state.acceleration_m_s2 == Vector2(0.0, 0.0)
    assert simulation.state.mass_kg == replacement.mass_kg
    assert simulation.state.phase is FlightPhase.READY
    assert simulation.state.has_lifted_off
    assert simulation.trajectory == (simulation.state,)
    assert simulation.accumulator_s == 0.0
    assert simulation.physics_step_count == 0
    assert not simulation.is_running
    assert not simulation.is_paused


def test_config_is_getter_only_but_headless_valid_values_exceeding_ui_bounds_work() -> None:
    simulation = Simulation()
    replacement = SimulationConfig(mass_kg=20.0)

    with pytest.raises(AttributeError):
        simulation.config = replacement  # type: ignore[misc]

    assert simulation.replace_ready_config(replacement)
    assert simulation.config.mass_kg == 20.0


@pytest.mark.parametrize("phase", ["running", "paused", "coast", "landed"])
def test_config_replacement_is_complete_noop_outside_ready(phase: str) -> None:
    if phase == "coast":
        simulation = Simulation(
            SimulationConfig(
                thrust_curve=ThrustCurve.zero(),
                gravity_m_s2=0.0,
                initial_position_m=Vector2(0.0, 1.0),
            )
        )
        simulation.launch()
        assert simulation.state.phase is FlightPhase.COAST
    else:
        simulation = Simulation()
        simulation.launch()
        if phase == "paused":
            simulation.toggle_pause()
            assert simulation.is_paused
        elif phase == "landed":
            for _ in range(1000):
                if not simulation.step():
                    break
            assert simulation.is_finished

    before = _simulation_snapshot(simulation)
    replacement = SimulationConfig(mass_kg=0.5)

    assert not simulation.replace_ready_config(replacement)
    assert _simulation_snapshot(simulation) == before


@pytest.mark.parametrize(
    ("identifier", "parameter", "direction", "expected"),
    [
        ("mass_kg.decrease", SetupParameter.MASS, -1, 0.9),
        ("mass_kg.increase", SetupParameter.MASS, 1, 1.1),
        (
            "launch_angle_rad.decrease",
            SetupParameter.LAUNCH_ANGLE,
            -1,
            math.radians(45.0),
        ),
        (
            "launch_angle_rad.increase",
            SetupParameter.LAUNCH_ANGLE,
            1,
            math.radians(55.0),
        ),
        (
            "drag_coefficient.decrease",
            SetupParameter.DRAG_COEFFICIENT,
            -1,
            0.70,
        ),
        (
            "drag_coefficient.increase",
            SetupParameter.DRAG_COEFFICIENT,
            1,
            0.80,
        ),
        (
            "reference_area_m2.decrease",
            SetupParameter.REFERENCE_AREA,
            -1,
            0.009,
        ),
        (
            "reference_area_m2.increase",
            SetupParameter.REFERENCE_AREA,
            1,
            0.011,
        ),
        (
            "air_density_kg_m3.decrease",
            SetupParameter.AIR_DENSITY,
            -1,
            1.175,
        ),
        (
            "air_density_kg_m3.increase",
            SetupParameter.AIR_DENSITY,
            1,
            1.275,
        ),
        ("gravity_m_s2.decrease", SetupParameter.GRAVITY, -1, 9.56),
        ("gravity_m_s2.increase", SetupParameter.GRAVITY, 1, 10.06),
    ],
)
def test_every_visible_adjustment_hitbox_maps_to_only_its_literal_field(
    identifier: str,
    parameter: SetupParameter,
    direction: int,
    expected: float,
) -> None:
    pygame.init()
    try:
        curve = _custom_curve()
        simulation = Simulation(_midrange_config(curve))
        renderer = Renderer()
        control = _control(renderer, simulation, identifier)
        action = renderer.action_at(control.rect.center, simulation)
        before = simulation.config

        assert action == AppAction(
            AppActionKind.ADJUST_SETUP, parameter, direction
        )
        assert dispatch_action(action, simulation, renderer)
        assert getattr(simulation.config, parameter.value) == expected
        for config_field in fields(SimulationConfig):
            if config_field.name != parameter.value:
                assert getattr(simulation.config, config_field.name) == getattr(
                    before, config_field.name
                )
        assert simulation.config.thrust_curve is curve
    finally:
        pygame.quit()


def test_primary_reset_and_restore_hitboxes_return_exact_typed_actions() -> None:
    pygame.init()
    try:
        simulation = Simulation(_midrange_config())
        renderer = Renderer()
        expected = {
            "primary": AppAction(AppActionKind.PRIMARY),
            "reset_flight": AppAction(AppActionKind.RESET_FLIGHT),
            "restore_defaults": AppAction(AppActionKind.RESTORE_DEFAULTS),
        }

        for identifier, action in expected.items():
            control = _control(renderer, simulation, identifier)
            assert renderer.action_at(control.rect.center, simulation) == action
    finally:
        pygame.quit()


@pytest.mark.parametrize(
    ("phase", "primary_label"),
    [
        ("running", "PAUSE"),
        ("paused", "RESUME"),
        ("coast", "PAUSE"),
        ("landed", "FLIGHT COMPLETE"),
    ],
)
def test_visible_setup_controls_lock_in_every_nonready_ui_state(
    phase: str, primary_label: str
) -> None:
    pygame.init()
    try:
        if phase == "coast":
            simulation = Simulation(
                replace(
                    _midrange_config(),
                    thrust_curve=ThrustCurve.zero(),
                    gravity_m_s2=0.0,
                    initial_velocity_m_s=Vector2(0.25, 0.0),
                )
            )
        else:
            simulation = Simulation(_midrange_config())
        simulation.launch()
        if phase == "paused":
            simulation.toggle_pause()
        elif phase == "landed":
            for _ in range(1000):
                if not simulation.step():
                    break
        renderer = Renderer()
        controls = renderer.setup_controls(simulation)

        for control in controls:
            if (
                control.action.kind is AppActionKind.ADJUST_SETUP
                or control.action.kind is AppActionKind.RESTORE_DEFAULTS
            ):
                assert not control.enabled
                assert renderer.action_at(control.rect.center, simulation) is None
        primary = _control(renderer, simulation, "primary")
        assert primary.label == primary_label
        assert primary.enabled is (phase != "landed")

        simulation.reset()
        reset_controls = renderer.setup_controls(simulation)
        assert _control(renderer, simulation, "restore_defaults").enabled
        for parameter in SetupParameter:
            assert any(
                control.enabled
                for control in reset_controls
                if control.action.parameter is parameter
            )
    finally:
        pygame.quit()


def test_real_mouse_and_keyboard_events_reach_the_common_dispatcher() -> None:
    pygame.init()
    try:
        simulation = Simulation()
        renderer = Renderer()
        primary = _control(renderer, simulation, "primary")
        mouse_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": primary.rect.center},
        )
        key_event = pygame.event.Event(
            pygame.KEYDOWN, {"key": pygame.K_SPACE}
        )

        with patch("rocket_sim.app.dispatch_action", return_value=True) as spy:
            assert handle_event(mouse_event, simulation, renderer)
            assert handle_event(key_event, simulation, renderer)

        assert [call.args[0] for call in spy.call_args_list] == [
            AppAction(AppActionKind.PRIMARY),
            AppAction(AppActionKind.PRIMARY),
        ]
    finally:
        pygame.quit()


def test_mouse_primary_transitions_match_space_and_mouse_ignores_invalid_clicks() -> None:
    pygame.init()
    try:
        simulation = Simulation()
        renderer = Renderer()
        primary_position = _control(renderer, simulation, "primary").rect.center

        assert handle_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": 1, "pos": primary_position},
            ),
            simulation,
            renderer,
        )
        assert simulation.is_running
        assert handle_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE}),
            simulation,
            renderer,
        )
        assert simulation.is_paused
        resume_position = _control(renderer, simulation, "primary").rect.center
        assert handle_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": 1, "pos": resume_position},
            ),
            simulation,
            renderer,
        )
        assert simulation.is_running

        before = _simulation_snapshot(simulation)
        for button, position in ((3, resume_position), (1, (799, 719))):
            assert handle_event(
                pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN,
                    {"button": button, "pos": position},
                ),
                simulation,
                renderer,
            )
        assert _simulation_snapshot(simulation) == before
    finally:
        pygame.quit()


@pytest.mark.parametrize("phase", ["running", "paused", "landed"])
def test_direct_setup_and_restore_actions_are_locked_until_reset(phase: str) -> None:
    simulation = Simulation(_midrange_config())
    simulation.launch()
    if phase == "paused":
        simulation.toggle_pause()
    elif phase == "landed":
        for _ in range(1000):
            if not simulation.step():
                break
        assert simulation.is_finished

    actions = [
        AppAction(AppActionKind.ADJUST_SETUP, parameter, direction)
        for parameter in SetupParameter
        for direction in (-1, 1)
    ]
    actions.append(AppAction(AppActionKind.RESTORE_DEFAULTS))
    for action in actions:
        before = _simulation_snapshot(simulation)
        assert dispatch_action(action, simulation)
        assert _simulation_snapshot(simulation) == before

    dispatch_action(AppAction(AppActionKind.RESET_FLIGHT), simulation)
    assert simulation.state.phase is FlightPhase.READY
    old_mass = simulation.config.mass_kg
    dispatch_action(
        AppAction(AppActionKind.ADJUST_SETUP, SetupParameter.MASS, 1),
        simulation,
    )
    assert simulation.config.mass_kg == old_mass + 0.1


def test_reset_preserves_selected_config_and_restore_recreates_exact_defaults() -> None:
    curve = _custom_curve()
    selected = replace(
        _midrange_config(curve),
        physics_dt_s=0.023,
        initial_position_m=Vector2(1.0, 2.0),
        initial_velocity_m_s=Vector2(3.0, 4.0),
    )
    simulation = Simulation(selected)
    simulation.launch()
    simulation.step()
    selected_identity = id(simulation.config)

    dispatch_action(AppAction(AppActionKind.RESET_FLIGHT), simulation)

    assert simulation.state.phase is FlightPhase.READY
    assert simulation.config is selected
    assert id(simulation.config) == selected_identity
    assert simulation.config.thrust_curve is curve

    dispatch_action(AppAction(AppActionKind.RESTORE_DEFAULTS), simulation)

    assert simulation.config == SimulationConfig()
    assert simulation.config.thrust_curve is not curve
    assert simulation.state.phase is FlightPhase.READY
    assert simulation.trajectory == (simulation.state,)


def test_mouse_reset_has_same_selected_config_semantics_as_keyboard_r() -> None:
    pygame.init()
    try:
        selected = _midrange_config()
        mouse_simulation = Simulation(selected)
        key_simulation = Simulation(selected)
        renderer = Renderer()
        for simulation in (mouse_simulation, key_simulation):
            simulation.launch()
            simulation.step()

        reset_position = _control(
            renderer, mouse_simulation, "reset_flight"
        ).rect.center
        handle_event(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": 1, "pos": reset_position},
            ),
            mouse_simulation,
            renderer,
        )
        handle_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r}),
            key_simulation,
            renderer,
        )

        assert _simulation_snapshot(mouse_simulation) == _simulation_snapshot(
            key_simulation
        )
        assert mouse_simulation.config is selected
        assert key_simulation.config is selected
    finally:
        pygame.quit()


def test_nondefault_selected_run_is_deterministic_after_reset() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.2,
            launch_angle_rad=math.radians(75.0),
            drag_coefficient=0.9,
            reference_area_m2=0.015,
            air_density_kg_m3=1.0,
            gravity_m_s2=8.0,
        )
    )
    frame_durations = (0.016, 0.004, 0.021, 0.013, 0.017)

    simulation.launch()
    for elapsed_s in frame_durations:
        simulation.advance_elapsed(elapsed_s)
    first = (
        simulation.state,
        simulation.trajectory,
        simulation.current_forces,
        simulation.physics_step_count,
    )

    simulation.reset()
    simulation.launch()
    for elapsed_s in frame_durations:
        simulation.advance_elapsed(elapsed_s)

    assert (
        simulation.state,
        simulation.trajectory,
        simulation.current_forces,
        simulation.physics_step_count,
    ) == first


def test_untouched_gui_defaults_reproduce_explicit_prompt04_default_flight() -> None:
    gui_default = Simulation()
    explicit_default = Simulation(SimulationConfig())

    for simulation in (gui_default, explicit_default):
        simulation.launch()
        for _ in range(1000):
            if not simulation.step():
                break

    assert gui_default.config == explicit_default.config
    assert gui_default.state == explicit_default.state
    assert gui_default.trajectory == explicit_default.trajectory
    assert gui_default.current_forces == explicit_default.current_forces
    assert gui_default.physics_step_count == explicit_default.physics_step_count


def test_mass_edit_reaches_production_acceleration() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=1.1,
            thrust_curve=_custom_curve(),
            launch_angle_rad=0.0,
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    dispatch_action(
        AppAction(AppActionKind.ADJUST_SETUP, SetupParameter.MASS, -1),
        simulation,
    )
    simulation.launch()

    assert simulation.config.mass_kg == 1.0
    assert simulation.state.acceleration_m_s2 == Vector2(10.0, 0.0)


def test_angle_edit_reaches_production_thrust_vector_in_radians() -> None:
    simulation = Simulation(
        SimulationConfig(
            thrust_curve=_custom_curve(),
            launch_angle_rad=math.radians(25.0),
            gravity_m_s2=0.0,
            air_density_kg_m3=0.0,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    dispatch_action(
        AppAction(
            AppActionKind.ADJUST_SETUP, SetupParameter.LAUNCH_ANGLE, 1
        ),
        simulation,
    )
    simulation.launch()

    assert simulation.config.launch_angle_rad == math.radians(30.0)
    assert simulation.current_forces.thrust_n.x == pytest.approx(
        5.0 * math.sqrt(3.0), abs=1e-12
    )
    assert simulation.current_forces.thrust_n.y == pytest.approx(5.0, abs=1e-12)


@pytest.mark.parametrize(
    ("parameter", "start", "expected"),
    [
        (SetupParameter.AIR_DENSITY, 0.80, 0.85),
        (SetupParameter.DRAG_COEFFICIENT, 0.40, 0.45),
        (SetupParameter.REFERENCE_AREA, 0.020, 0.021),
    ],
)
def test_each_drag_setup_field_reaches_production_force(
    parameter: SetupParameter, start: float, expected: float
) -> None:
    values = {
        SetupParameter.AIR_DENSITY.value: 0.80,
        SetupParameter.DRAG_COEFFICIENT.value: 0.40,
        SetupParameter.REFERENCE_AREA.value: 0.020,
    }
    values[parameter.value] = start
    simulation = Simulation(
        SimulationConfig(
            thrust_curve=ThrustCurve.zero(),
            gravity_m_s2=0.0,
            initial_position_m=Vector2(0.0, 10.0),
            initial_velocity_m_s=Vector2(3.0, 4.0),
            **values,
        )
    )
    dispatch_action(
        AppAction(AppActionKind.ADJUST_SETUP, parameter, 1), simulation
    )
    simulation.launch()

    rho = 0.85 if parameter is SetupParameter.AIR_DENSITY else 0.80
    cd = 0.45 if parameter is SetupParameter.DRAG_COEFFICIENT else 0.40
    area = 0.021 if parameter is SetupParameter.REFERENCE_AREA else 0.020
    factor = -0.5 * rho * cd * area * 5.0
    assert getattr(simulation.config, parameter.value) == expected
    assert simulation.current_forces.drag_n.x == pytest.approx(
        factor * 3.0, abs=1e-12
    )
    assert simulation.current_forces.drag_n.y == pytest.approx(
        factor * 4.0, abs=1e-12
    )


def test_gravity_edit_reaches_production_gravity_force() -> None:
    simulation = Simulation(
        SimulationConfig(
            mass_kg=2.0,
            thrust_curve=ThrustCurve.zero(),
            gravity_m_s2=3.0,
            air_density_kg_m3=0.0,
            initial_position_m=Vector2(0.0, 1.0),
        )
    )
    dispatch_action(
        AppAction(AppActionKind.ADJUST_SETUP, SetupParameter.GRAVITY, 1),
        simulation,
    )
    simulation.launch()

    assert simulation.config.gravity_m_s2 == 3.25
    assert simulation.current_forces.gravity_n == Vector2(0.0, -6.5)


@pytest.mark.parametrize("parameter", list(SetupParameter))
def test_all_setup_bounds_clamp_both_directions_and_steps_are_reversible(
    parameter: SetupParameter,
) -> None:
    spec = next(
        candidate
        for candidate in SETUP_PARAMETER_SPECS
        if candidate.parameter is parameter
    )
    minimum_config = _config_with_display_value(parameter, spec.minimum)
    maximum_config = _config_with_display_value(parameter, spec.maximum)
    default = SimulationConfig()

    assert adjusted_setup_config(minimum_config, parameter, -1) is minimum_config
    assert adjusted_setup_config(maximum_config, parameter, 1) is maximum_config

    stepped = default
    for _ in range(500):
        stepped = adjusted_setup_config(stepped, parameter, 1)
    assert setup_display_value(stepped, parameter) == spec.maximum

    reversible_start = (
        _config_with_display_value(parameter, 50.0)
        if parameter is SetupParameter.LAUNCH_ANGLE
        else default
    )
    up_then_down = adjusted_setup_config(
        adjusted_setup_config(reversible_start, parameter, 1), parameter, -1
    )
    assert setup_display_value(up_then_down, parameter) == setup_display_value(
        reversible_start, parameter
    )


def test_setup_text_tracks_edit_reset_and_restore_without_a_cached_store() -> None:
    simulation = Simulation()
    before = {row.parameter: row.value for row in setup_display_rows(simulation.config)}
    dispatch_action(
        AppAction(AppActionKind.ADJUST_SETUP, SetupParameter.MASS, 1), simulation
    )
    edited = {row.parameter: row.value for row in setup_display_rows(simulation.config)}
    simulation.launch()
    simulation.reset()
    reset = {row.parameter: row.value for row in setup_display_rows(simulation.config)}
    dispatch_action(AppAction(AppActionKind.RESTORE_DEFAULTS), simulation)
    restored = {row.parameter: row.value for row in setup_display_rows(simulation.config)}

    assert before[SetupParameter.MASS] == "1.00 kg"
    assert edited[SetupParameter.MASS] == "1.10 kg"
    assert reset == edited
    assert restored == before


def test_drawn_setup_labels_and_values_come_from_distinctive_production_config() -> None:
    class RecordingFont:
        def __init__(self, rendered_text: list[str]) -> None:
            self.rendered_text = rendered_text

        def render(
            self,
            text: str,
            antialias: bool,
            color: tuple[int, int, int],
        ) -> pygame.Surface:
            del antialias, color
            self.rendered_text.append(text)
            return pygame.Surface((max(1, len(text) * 5), 14), pygame.SRCALPHA)

    pygame.init()
    try:
        config = SimulationConfig(
            mass_kg=2.3,
            thrust_curve=ThrustCurve.constant(7.0, 2.0),
            launch_angle_rad=math.radians(35.0),
            gravity_m_s2=3.5,
            air_density_kg_m3=0.85,
            drag_coefficient=1.15,
            reference_area_m2=0.023,
            physics_dt_s=0.037,
        )
        simulation = Simulation(config)
        renderer = Renderer()
        rendered_text: list[str] = []
        recording_font = RecordingFont(rendered_text)
        renderer._font = recording_font  # type: ignore[assignment]
        renderer._small_font = recording_font  # type: ignore[assignment]
        renderer._heading_font = recording_font  # type: ignore[assignment]

        renderer.draw(pygame.Surface((1200, 720)), simulation)

        for expected in (
            "Mass (constant/run)",
            "2.30 kg",
            "Fixed thrust direction",
            "35 deg",
            "Drag coefficient Cd",
            "1.15",
            "Reference area",
            "0.023 m^2",
            "Air density",
            "0.850 kg/m^3",
            "Gravity",
            "3.50 m/s^2",
            "MOTOR (read-only): current sampled curve",
            "Total impulse 14.000 N*s   Physics dt: 0.037 s",
        ):
            assert expected in rendered_text
    finally:
        pygame.quit()


def test_launch_preview_has_literal_30_degree_screen_geometry_and_draw_wiring() -> None:
    assert launch_direction_preview_endpoint(
        (100, 100), math.radians(30.0), 100.0
    ) == (187, 50)

    pygame.init()
    try:
        simulation = Simulation(
            SimulationConfig(launch_angle_rad=math.radians(30.0))
        )
        renderer = Renderer()
        surface = pygame.Surface((1200, 720))
        with patch(
            "rocket_sim.rendering.launch_direction_preview_endpoint",
            wraps=launch_direction_preview_endpoint,
        ) as preview_spy:
            renderer.draw(surface, simulation)

        preview_spy.assert_called_once()
        assert preview_spy.call_args.args[1] == simulation.config.launch_angle_rad
    finally:
        pygame.quit()


def test_draw_and_hit_testing_do_not_mutate_any_public_simulation_observable() -> None:
    pygame.init()
    try:
        simulation = Simulation()
        simulation.launch()
        simulation.step()
        simulation.toggle_pause()
        renderer = Renderer()
        surface = pygame.Surface((1200, 720))
        before = _simulation_snapshot(simulation)

        renderer.draw(surface, simulation)
        for control in renderer.setup_controls(simulation):
            renderer.action_at(control.rect.center, simulation)

        assert _simulation_snapshot(simulation) == before
    finally:
        pygame.quit()
