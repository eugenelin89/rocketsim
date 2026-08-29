import math

import pytest

from rocket_sim import SimulationConfig, Vector2


def test_zero_valued_limiting_parameters_are_valid() -> None:
    config = SimulationConfig(
        thrust_n=0.0,
        burn_time_s=0.0,
        gravity_m_s2=0.0,
        air_density_kg_m3=0.0,
        drag_coefficient=0.0,
        reference_area_m2=0.0,
    )

    assert config.thrust_n == 0.0
    assert config.burn_time_s == 0.0
    assert config.gravity_m_s2 == 0.0
    assert config.air_density_kg_m3 == 0.0
    assert config.drag_coefficient == 0.0
    assert config.reference_area_m2 == 0.0


def test_default_aerodynamic_values_are_documented_educational_constants() -> None:
    config = SimulationConfig()

    assert config.air_density_kg_m3 == 1.225
    assert config.drag_coefficient == 0.75
    assert config.reference_area_m2 == 0.01


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
        ("air_density_kg_m3", -1.0),
        ("drag_coefficient", -1.0),
        ("reference_area_m2", -1.0),
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
        "air_density_kg_m3",
        "drag_coefficient",
        "reference_area_m2",
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
