"""Immutable sampled thrust curves and exact piecewise-linear impulse metrics."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import Iterable
import math


@dataclass(frozen=True, slots=True)
class ThrustSample:
    """One thrust-curve knot in SI units."""

    time_s: float
    thrust_n: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.time_s):
            raise ValueError("thrust sample time_s must be finite")
        if not math.isfinite(self.thrust_n):
            raise ValueError("thrust sample thrust_n must be finite")
        if self.time_s < 0.0:
            raise ValueError("thrust sample time_s must be non-negative")
        if self.thrust_n < 0.0:
            raise ValueError("thrust sample thrust_n must be non-negative")


@dataclass(frozen=True, slots=True, init=False)
class ThrustCurve:
    """Validated piecewise-linear thrust with a half-open burn interval."""

    samples: tuple[ThrustSample, ...]
    _sample_times_s: tuple[float, ...]
    _prefix_impulse_ns: tuple[float, ...]

    def __init__(self, samples: Iterable[ThrustSample]) -> None:
        owned_samples = tuple(samples)
        if not owned_samples:
            raise ValueError("a thrust curve requires at least one sample")
        if any(not isinstance(sample, ThrustSample) for sample in owned_samples):
            raise TypeError("thrust curve samples must be ThrustSample values")
        if owned_samples[0].time_s != 0.0:
            raise ValueError("the first thrust sample time must be exactly zero")
        for before, after in zip(owned_samples, owned_samples[1:], strict=False):
            if after.time_s <= before.time_s:
                raise ValueError("thrust sample times must be strictly increasing")
        if len(owned_samples) == 1 and owned_samples[0].thrust_n != 0.0:
            raise ValueError("a zero-duration curve must contain only zero thrust")

        prefix_impulse = [0.0]
        for before, after in zip(owned_samples, owned_samples[1:], strict=False):
            prefix_impulse.append(
                prefix_impulse[-1]
                + 0.5
                * (before.thrust_n + after.thrust_n)
                * (after.time_s - before.time_s)
            )

        object.__setattr__(self, "samples", owned_samples)
        object.__setattr__(
            self, "_sample_times_s", tuple(sample.time_s for sample in owned_samples)
        )
        object.__setattr__(self, "_prefix_impulse_ns", tuple(prefix_impulse))

    @classmethod
    def zero(cls) -> ThrustCurve:
        """Return the zero-duration, zero-thrust limiting curve."""

        return cls((ThrustSample(0.0, 0.0),))

    @classmethod
    def constant(cls, thrust_n: float, burn_duration_s: float) -> ThrustCurve:
        """Return constant thrust over ``0 <= t < burn_duration_s``."""

        if not math.isfinite(thrust_n) or thrust_n < 0.0:
            raise ValueError("constant thrust_n must be finite and non-negative")
        if not math.isfinite(burn_duration_s) or burn_duration_s < 0.0:
            raise ValueError(
                "constant burn_duration_s must be finite and non-negative"
            )
        if burn_duration_s == 0.0:
            if thrust_n != 0.0:
                raise ValueError("positive thrust requires a positive burn duration")
            return cls.zero()
        return cls(
            (
                ThrustSample(0.0, thrust_n),
                ThrustSample(burn_duration_s, thrust_n),
            )
        )

    @property
    def burn_duration_s(self) -> float:
        return self.samples[-1].time_s

    @property
    def total_impulse_ns(self) -> float:
        return self._prefix_impulse_ns[-1]

    @property
    def average_thrust_n(self) -> float:
        if self.burn_duration_s == 0.0:
            return 0.0
        return self.total_impulse_ns / self.burn_duration_s

    @property
    def peak_thrust_n(self) -> float:
        """Return the maximum stored ordinate, the curve's thrust supremum."""

        return max(sample.thrust_n for sample in self.samples)

    def thrust_at(self, time_s: float) -> float:
        """Return instantaneous thrust, zero outside the half-open burn."""

        self._validate_query_time(time_s)
        if time_s < 0.0 or time_s >= self.burn_duration_s:
            return 0.0

        left_index = bisect_right(self._sample_times_s, time_s) - 1
        left = self.samples[left_index]
        right = self.samples[left_index + 1]
        fraction = (time_s - left.time_s) / (right.time_s - left.time_s)
        return left.thrust_n + fraction * (right.thrust_n - left.thrust_n)

    def delivered_impulse_ns(self, time_s: float) -> float:
        """Return exact curve impulse delivered through the clamped time."""

        self._validate_query_time(time_s)
        if time_s <= 0.0 or self.burn_duration_s == 0.0:
            return 0.0
        if time_s >= self.burn_duration_s:
            return self.total_impulse_ns

        left_index = bisect_right(self._sample_times_s, time_s) - 1
        left = self.samples[left_index]
        right = self.samples[left_index + 1]
        duration_s = time_s - left.time_s
        slope_n_s = (right.thrust_n - left.thrust_n) / (
            right.time_s - left.time_s
        )
        partial_impulse_ns = (
            left.thrust_n * duration_s
            + 0.5 * slope_n_s * duration_s * duration_s
        )
        return self._prefix_impulse_ns[left_index] + partial_impulse_ns

    def impulse_between_ns(self, start_time_s: float, end_time_s: float) -> float:
        """Return exact curve impulse over an ordered time interval."""

        self._validate_query_time(start_time_s)
        self._validate_query_time(end_time_s)
        if end_time_s < start_time_s:
            raise ValueError("impulse interval end must not precede its start")
        return self.delivered_impulse_ns(
            end_time_s
        ) - self.delivered_impulse_ns(start_time_s)

    def knots_strictly_between(
        self, start_time_s: float, end_time_s: float
    ) -> tuple[float, ...]:
        """Return configured knot times strictly inside an ordered interval."""

        self._validate_query_time(start_time_s)
        self._validate_query_time(end_time_s)
        if end_time_s < start_time_s:
            raise ValueError("knot interval end must not precede its start")
        return tuple(
            time_s
            for time_s in self._sample_times_s
            if start_time_s < time_s < end_time_s
        )

    @staticmethod
    def _validate_query_time(time_s: float) -> None:
        if not math.isfinite(time_s):
            raise ValueError("thrust-curve query time must be finite")


# Self-authored educational data, not measurements from a certified motor.
# The nonzero ignition value keeps the default ground launch admissible without
# adding pad, rail, or support-force physics.
DEFAULT_EDUCATIONAL_THRUST_CURVE = ThrustCurve(
    (
        ThrustSample(0.00, 12.0),
        ThrustSample(0.05, 28.0),
        ThrustSample(0.12, 24.0),
        ThrustSample(0.35, 20.0),
        ThrustSample(0.70, 16.0),
        ThrustSample(0.95, 8.0),
        ThrustSample(1.05, 0.0),
    )
)
