import math

import pytest

from rocket_sim import SimulationConfig, Vector2


def test_zero_valued_limiting_parameters_are_valid() -> None:
    config = SimulationConfig(thrust_n=0.0, burn_time_s=0.0, gravity_m_s2=0.0)

    assert config.thrust_n == 0.0
    assert config.burn_time_s == 0.0
    assert config.gravity_m_s2 == 0.0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("mass_kg", 0.0),
        ("mass_kg", -1.0),
        ("physics_dt_s", 0.0),
        ("physics_dt_s", -0.01),
        ("thrust_n", -1.0),
        ("burn_time_s", -1.0),
        ("gravity_m_s2", -1.0),
    ],
)
def test_invalid_physical_ranges_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        SimulationConfig(**{field: value})


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
@pytest.mark.parametrize(
    "field",
    [
        "mass_kg",
        "physics_dt_s",
        "thrust_n",
        "burn_time_s",
        "gravity_m_s2",
        "launch_angle_rad",
    ],
)
def test_non_finite_scalars_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        SimulationConfig(**{field: value})


@pytest.mark.parametrize("component", [math.nan, math.inf, -math.inf])
def test_non_finite_vector_components_are_rejected(component: float) -> None:
    with pytest.raises(ValueError):
        Vector2(component, 0.0)
    with pytest.raises(ValueError):
        Vector2(0.0, component)


def test_initial_altitude_below_ground_is_rejected() -> None:
    with pytest.raises(ValueError, match="altitude"):
        SimulationConfig(initial_position_m=Vector2(0.0, -0.01))
