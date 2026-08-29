import math

import pytest

from rocket_sim import Simulation, SimulationConfig


def _run_partitioned(
    total_s: float,
    fps: int,
    air_density_kg_m3: float,
    physics_dt_s: float = 0.01,
    burn_time_s: float = 1.0,
) -> Simulation:
    simulation = Simulation(
        SimulationConfig(
            air_density_kg_m3=air_density_kg_m3,
            physics_dt_s=physics_dt_s,
            burn_time_s=burn_time_s,
        )
    )
    simulation.launch()
    frame_s = 1.0 / fps
    elapsed_s = 0.0
    while elapsed_s + frame_s < total_s:
        simulation.advance_elapsed(frame_s)
        elapsed_s += frame_s
    simulation.advance_elapsed(total_s - elapsed_s)
    return simulation


def test_fixed_physics_results_are_independent_of_30_60_144_fps_partitions() -> None:
    simulations = [_run_partitioned(0.5, fps, 0.0) for fps in (30, 60, 144)]

    for simulation in simulations:
        assert simulation.physics_step_count == 50
        assert simulation.state.time_s == pytest.approx(0.5, abs=1e-12)
    assert simulations[0].state == simulations[1].state == simulations[2].state
    assert (
        simulations[0].trajectory
        == simulations[1].trajectory
        == simulations[2].trajectory
    )


def test_active_drag_results_are_independent_of_30_60_144_fps_partitions() -> None:
    simulations = [
        _run_partitioned(
            0.5,
            fps,
            1.225,
            physics_dt_s=0.125,
            burn_time_s=0.25,
        )
        for fps in (30, 60, 144)
    ]

    for simulation in simulations:
        assert simulation.physics_step_count == 4
        assert simulation.state.time_s == pytest.approx(0.5, abs=1e-12)
    assert simulations[0].state == simulations[1].state == simulations[2].state
    assert (
        simulations[0].trajectory
        == simulations[1].trajectory
        == simulations[2].trajectory
    )


def test_zero_elapsed_never_advances_even_with_very_small_valid_timestep() -> None:
    simulation = Simulation(SimulationConfig(physics_dt_s=1e-15))
    simulation.launch()

    assert simulation.advance_elapsed(0.0) == 0
    assert simulation.physics_step_count == 0
    assert simulation.state.time_s == 0.0


def test_representably_subthreshold_elapsed_time_does_not_advance() -> None:
    dt = 0.01
    simulation = Simulation(SimulationConfig(physics_dt_s=dt))
    simulation.launch()

    assert simulation.advance_elapsed(math.nextafter(dt, 0.0)) == 0
    assert simulation.physics_step_count == 0
    assert simulation.state.time_s == 0.0
