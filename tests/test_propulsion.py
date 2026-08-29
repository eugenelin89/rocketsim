from dataclasses import FrozenInstanceError
import math

import pytest

from rocket_sim import (
    DEFAULT_EDUCATIONAL_THRUST_CURVE,
    ThrustCurve,
    ThrustSample,
)


def _curve(*samples: tuple[float, float]) -> ThrustCurve:
    return ThrustCurve(ThrustSample(time_s, thrust_n) for time_s, thrust_n in samples)


def test_curve_defensively_owns_an_immutable_sample_tuple() -> None:
    source = [ThrustSample(0.0, 2.0), ThrustSample(1.0, 0.0)]
    curve = ThrustCurve(source)
    source.append(ThrustSample(2.0, 0.0))

    assert curve.samples == (ThrustSample(0.0, 2.0), ThrustSample(1.0, 0.0))
    with pytest.raises(FrozenInstanceError):
        curve.samples = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        curve.samples[0].thrust_n = 3.0  # type: ignore[misc]


@pytest.mark.parametrize(
    "samples",
    [
        (),
        (ThrustSample(0.1, 0.0), ThrustSample(1.0, 0.0)),
        (ThrustSample(0.0, 1.0),),
        (ThrustSample(0.0, 1.0), ThrustSample(0.0, 2.0)),
        (ThrustSample(0.0, 1.0), ThrustSample(0.5, 2.0), ThrustSample(0.4, 0.0)),
    ],
)
def test_invalid_curve_structure_is_rejected(
    samples: tuple[ThrustSample, ...],
) -> None:
    with pytest.raises(ValueError):
        ThrustCurve(samples)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_sample_times_are_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="time_s"):
        ThrustSample(value, 0.0)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_sample_thrust_is_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="thrust_n"):
        ThrustSample(0.0, value)


def test_negative_sample_time_and_thrust_are_rejected() -> None:
    with pytest.raises(ValueError, match="time_s"):
        ThrustSample(-0.1, 0.0)
    with pytest.raises(ValueError, match="thrust_n"):
        ThrustSample(0.0, -0.1)


def test_non_sample_values_are_rejected() -> None:
    with pytest.raises(TypeError, match="ThrustSample"):
        ThrustCurve(((0.0, 1.0), (1.0, 0.0)))  # type: ignore[arg-type]


def test_zero_curve_is_safe_for_every_metric() -> None:
    curve = ThrustCurve.zero()

    assert curve.samples == (ThrustSample(0.0, 0.0),)
    assert curve.burn_duration_s == 0.0
    assert curve.thrust_at(-1.0) == 0.0
    assert curve.thrust_at(0.0) == 0.0
    assert curve.thrust_at(1.0) == 0.0
    assert curve.delivered_impulse_ns(-1.0) == 0.0
    assert curve.delivered_impulse_ns(1.0) == 0.0
    assert curve.total_impulse_ns == 0.0
    assert curve.average_thrust_n == 0.0
    assert curve.peak_thrust_n == 0.0


def test_constant_curve_preserves_nonzero_burn_end_left_limit_in_impulse() -> None:
    curve = ThrustCurve.constant(5.0, 2.0)

    assert curve.samples == (ThrustSample(0.0, 5.0), ThrustSample(2.0, 5.0))
    assert curve.thrust_at(math.nextafter(2.0, 0.0)) == 5.0
    assert curve.thrust_at(2.0) == 0.0
    assert curve.total_impulse_ns == 10.0
    assert curve.delivered_impulse_ns(2.0) == 10.0
    assert curve.average_thrust_n == 5.0
    assert curve.peak_thrust_n == 5.0


def test_invalid_constant_curve_parameters_are_rejected() -> None:
    for thrust_n, duration_s in (
        (-1.0, 1.0),
        (math.inf, 1.0),
        (1.0, -1.0),
        (1.0, math.nan),
        (1.0, 0.0),
    ):
        with pytest.raises(ValueError):
            ThrustCurve.constant(thrust_n, duration_s)


def test_interpolation_and_half_open_boundaries_match_literal_oracle() -> None:
    curve = _curve((0.0, 2.0), (0.4, 6.0), (1.0, 4.0))

    assert curve.thrust_at(-0.1) == 0.0
    assert curve.thrust_at(0.0) == 2.0
    assert curve.thrust_at(0.2) == 4.0
    assert curve.thrust_at(0.4) == 6.0
    assert curve.thrust_at(0.7) == pytest.approx(5.0, abs=1e-12)
    assert curve.thrust_at(math.nextafter(1.0, 0.0)) == pytest.approx(
        4.0, abs=1e-12
    )
    assert curve.thrust_at(1.0) == 0.0
    assert curve.thrust_at(1.1) == 0.0


def test_triangle_rectangle_and_multisegment_impulses_are_exact() -> None:
    triangle = _curve((0.0, 0.0), (1.0, 6.0), (2.0, 0.0))
    rectangle = _curve((0.0, 5.0), (2.0, 5.0))
    multi = _curve((0.0, 2.0), (0.5, 6.0), (1.5, 4.0), (2.0, 8.0))

    assert triangle.total_impulse_ns == 6.0
    assert rectangle.total_impulse_ns == 10.0
    assert multi.total_impulse_ns == 10.0
    assert multi.delivered_impulse_ns(-1.0) == 0.0
    assert multi.delivered_impulse_ns(0.0) == 0.0
    assert multi.delivered_impulse_ns(0.25) == pytest.approx(0.75, abs=1e-12)
    assert multi.delivered_impulse_ns(0.5) == 2.0
    assert multi.delivered_impulse_ns(1.0) == pytest.approx(4.75, abs=1e-12)
    assert multi.delivered_impulse_ns(1.5) == 7.0
    assert multi.delivered_impulse_ns(1.75) == pytest.approx(8.25, abs=1e-12)
    assert multi.delivered_impulse_ns(2.0) == 10.0
    assert multi.delivered_impulse_ns(3.0) == 10.0
    assert multi.average_thrust_n == 5.0
    assert multi.peak_thrust_n == 8.0


def test_delivered_impulse_is_monotonic_and_interval_additive() -> None:
    curve = _curve((0.0, 0.0), (0.2, 7.0), (0.9, 3.0), (1.1, 0.0))
    times = (-1.0, 0.0, 0.1, 0.2, 0.6, 0.9, 1.1, 2.0)
    delivered = [curve.delivered_impulse_ns(time_s) for time_s in times]

    assert delivered == sorted(delivered)
    assert curve.impulse_between_ns(0.1, 0.9) == pytest.approx(
        curve.impulse_between_ns(0.1, 0.6)
        + curve.impulse_between_ns(0.6, 0.9),
        abs=1e-12,
    )
    with pytest.raises(ValueError, match="precede"):
        curve.impulse_between_ns(0.9, 0.1)


@pytest.mark.parametrize("method_name", ["thrust_at", "delivered_impulse_ns"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_query_times_are_rejected(
    method_name: str, value: float
) -> None:
    curve = ThrustCurve.constant(1.0, 1.0)
    with pytest.raises(ValueError, match="query time"):
        getattr(curve, method_name)(value)


def test_knot_selection_is_strict_and_ordered() -> None:
    curve = _curve((0.0, 1.0), (0.1, 2.0), (0.2, 3.0), (0.5, 0.0))

    assert curve.knots_strictly_between(0.0, 0.5) == (0.1, 0.2)
    assert curve.knots_strictly_between(0.1, 0.5) == (0.2,)
    assert curve.knots_strictly_between(0.2, 0.2) == ()


def test_default_synthetic_curve_metrics_match_independent_trapezoids() -> None:
    curve = DEFAULT_EDUCATIONAL_THRUST_CURVE
    expected_samples = (
        ThrustSample(0.00, 12.0),
        ThrustSample(0.05, 28.0),
        ThrustSample(0.12, 24.0),
        ThrustSample(0.35, 20.0),
        ThrustSample(0.70, 16.0),
        ThrustSample(0.95, 8.0),
        ThrustSample(1.05, 0.0),
    )
    independently_summed_areas_ns = 1.00 + 1.82 + 5.06 + 6.30 + 3.00 + 0.40

    assert curve.samples == expected_samples
    assert curve.burn_duration_s == 1.05
    assert curve.total_impulse_ns == pytest.approx(
        independently_summed_areas_ns, abs=1e-12
    )
    assert curve.peak_thrust_n == 28.0
    assert curve.average_thrust_n == pytest.approx(
        16.74285714285714, abs=1e-12
    )
