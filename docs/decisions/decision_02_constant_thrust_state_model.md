# Decision 02: Constant-thrust point-mass state model

- Date: 2026-08-27
- Status: accepted
- Related prompt: `docs/prompts/prompt_02_physics.md`
- Supersedes: none

## Decision

Milestone 1 represents the rocket as a constant-mass point with immutable recorded states containing time, 2D position, 2D velocity, instantaneous acceleration, mass, physical phase, and a liftoff flag. It applies only constant gravity and constant thrust at a fixed world angle during the half-open interval `0 <= t < burn_time`.

The default vertical case is `m = 1 kg`, `T = 20 N`, `burn_time = 1 s`, `g = 9.81 m/s²`, and `dt = 0.01 s`. All physics values use SI units and +y points upward.

## Context

Prompt 02 requires the smallest physical model that produces powered ascent, burnout, coast, descent, and landing while remaining analytically understandable. Constant mass intentionally excludes propellant depletion. A fixed world thrust direction intentionally excludes attitude dynamics.

## Options considered

- Store mass only in configuration or repeat it in each state. Repeating it makes the invariant visible in telemetry and history while configuration remains authoritative.
- Treat a non-lifting or under-resolved ground configuration as supported by a pad, allow negative altitude, or terminate at its initial state. Termination avoids inventing an unmodeled normal force or integrating underground.
- Derive displayed acceleration from the last interval or from the current time. Instantaneous current-time acceleration keeps exact-burnout telemetry consistent with coast phase.

## Rationale

The accepted model keeps every force physically named, preserves explicit units and signs, supports independent closed-form validation, and avoids speculative motor, contact, or attitude abstractions.

## Consequences and limits

- Mass is exactly constant throughout a run.
- At exact burnout, thrust is zero and telemetry reports coast acceleration.
- A ground start needs non-negative initial vertical velocity and a positive-altitude endpoint for its first constant-force numerical segment.
- A terminal state retains time-consistent thrust and acceleration at the instant of impact.
- Gravity-only and zero-thrust references start above ground when needed.
- The result is not a 3D, aerodynamic, calibrated, or engineering-grade prediction.

No prior decision is superseded.

## Later partial supersession

Decision 07 supersedes this record's independently configured constant-thrust/burn-duration propulsion representation and its `20 N` / `1 s` default. The constant-mass state representation, fixed world thrust direction, half-open motor interval, ground-boundary policy, and instantaneous resulting-state telemetry remain accepted. The two-sample rectangular `ThrustCurve` preserves the former constant-thrust model as a limiting case.
