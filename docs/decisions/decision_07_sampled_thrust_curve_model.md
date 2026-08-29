# Decision 07: Sampled thrust-curve propulsion model

- Date: 2026-08-29
- Status: accepted
- Related prompt: `docs/prompts/prompt_04_propulsion_learning.md`
- Supersedes: Decision 02's independently configured propulsion representation and default; its state model and other physical provisions remain accepted

## Decision

Prompt 04 replaces independently configurable constant thrust and burn duration with one immutable, authoritative piecewise-linear `ThrustCurve`. The curve owns validated `(time_s, thrust_n)` samples, begins at exactly zero time, uses strictly increasing later times, and derives burn duration from its final sample. The zero-duration limit is the single sample `(0,0)`.

Instantaneous thrust is linearly interpolated for `0 <= t < burn_end`, equals stored values at interior knots, and is zero before ignition and at/after burn end. A final nonzero stored sample remains the left-limit endpoint of the last trapezoid even though instantaneous thrust at exact burn end is zero.

Total and delivered motor impulse are exact geometric integrals of the stored curve. Average thrust is total impulse divided by positive burn duration, and stored peak thrust is the maximum sample ordinate—the represented curve's supremum. A unique nonzero terminal peak is a left-limit value rather than an attained value of the half-open instantaneous function. A two-sample rectangle is the Prompt 02–03 constant-thrust limit; the singleton zero curve is the zero-thrust limit.

Every fixed outer physics step is split at all strictly crossed curve knots. On each internal segment:

```text
J_T = exact piecewise-linear thrust impulse
F_other_start = F_gravity + F_drag(v_start)

v_next = v_start
         + (J_T / m) (cos(theta), sin(theta))
         + (F_other_start / m) dt

p_next = p_start + v_next dt
```

Current force and acceleration telemetry remains instantaneous at the resulting time and velocity. Mass and thrust direction remain constant.

The default is self-authored synthetic educational data:

```text
(0.00 s, 12 N)
(0.05 s, 28 N)
(0.12 s, 24 N)
(0.35 s, 20 N)
(0.70 s, 16 N)
(0.95 s,  8 N)
(1.05 s,  0 N)
```

It has `17.58 N*s` total impulse, `28 N` peak thrust, and `16.742857... N` average thrust. It begins above the default rocket's weight so the ground launch is admissible without pad/contact support. The originally proposed zero-at-ignition curve remains an airborne/zero-gravity educational validation example with `17.28 N*s`, not the ground default.

## Context and problem

The prior rectangular motor delivered correct constant thrust but could not represent ignition rise, changing thrust, peak versus average thrust, or motor impulse. Time-varying thrust also creates discontinuous interpolation slopes and knot boundaries that a start-value-only force evaluation would integrate incorrectly.

The proposed zero-at-ignition default delivers only `0.028 N*s` in the first `0.01 s`, less than the `0.0981 N*s` downward gravity impulse. Under the accepted no-pad/no-contact model, it would move below ground. Adding a clamp, hidden hold, or normal force would introduce a second physical effect. The launchable `12 N` initial sample is the smallest transparent scope correction; zero-at-ignition behavior remains demonstrable away from the ground boundary.

## Options considered

- Exact piecewise-linear impulse with internal knot segmentation, the selected model.
- Evaluate instantaneous thrust only at segment start, rejected because rising/falling impulse error becomes timestep-dependent.
- Add pad hold/release or normal-force physics, rejected as a new contact model outside Prompt 04.
- Preserve the original ground default through look-ahead, clamping, or discarded downward steps, rejected as hidden physics.
- Use an above-ground default, rejected because it would evade rather than resolve the intended launch scenario.
- Adopt a general motor database/import/plugin framework, rejected as unnecessary scope.

## Rationale

One immutable curve removes competing propulsion sources of truth. Exact trapezoidal impulse is analytically inspectable and makes the impulse–momentum limiting case independent of timestep. Knot splitting handles every curve interval and burn end deterministically while retaining the established fixed outer clock, semi-implicit position update, and explicit start-velocity drag.

The adjusted default keeps the intended synthetic shape, peak, and duration while remaining honest about the absence of launch support physics. Its metrics are independently derived and displayed from production data.

## Consequences and tradeoffs

- Motor impulse is exact for each completed segment of the stored polyline, but position, drag impulse, apogee, and impact remain numerical approximations.
- Curve knots become internal numerical boundaries. Redundant collinear samples can cause extra drag reevaluations and change a finite-timestep active-drag trajectory even when the mathematical thrust curve is unchanged.
- The outer accumulator and physics-step count remain based on the configured fixed timestep; internal knot states may add trajectory samples.
- Powered phase is the curve's half-open time interval, not a guarantee of positive instantaneous thrust.
- Ground impact remains interpolation of the discrete path; a powered impact is not an exact partial-impulse event solution.
- The model omits variable mass, propellant depletion, specific impulse, exhaust velocity, motor chemistry, measured motor import, and thrust-vector control.

## Related prompt records

- `docs/prompts/prompt_04_propulsion_learning.md`

## Superseding decision

Decision 07 partially supersedes Decision 02 as stated above. Decision 02's constant-mass state model, fixed thrust direction, ground-boundary policy, and resulting-state telemetry remain accepted.
