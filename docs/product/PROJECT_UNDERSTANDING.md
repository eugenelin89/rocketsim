# Project Understanding

## Purpose and current milestone

RocketSim is a trustworthy, understandable 2D model-rocket simulator rather than an engineering-grade launch predictor. Prompt 02 completes the first powered point-mass flight milestone: a visible Pygame application backed by a headless, deterministic physics core and independent numerical evidence.

Prompt 03 has not begun.

## Implemented model

The rocket is a constant-mass point in a 2D flat world. Internally, all quantities use SI units, +x points right, +y points upward, and the ground is `y = 0`.

The only forces are:

- constant gravity `(0, -m g)`; and
- constant thrust `T(cos(theta), sin(theta))` during `0 <= t < burn_time`.

The default configuration is `m = 1 kg`, `T = 20 N`, `burn_time = 1 s`, `theta = 90 degrees`, `g = 9.81 m/s²`, and `dt = 0.01 s`. It is intentionally capable of liftoff. A ground start is accepted only when its initial vertical velocity is non-negative and its first constant-force numerical segment ends above ground. Otherwise it terminates at the initial ground state without recording negative altitude; no pad normal-force model is claimed.

## Implemented structure

```text
src/rocket_sim/config.py       validated immutable configuration and neutral Vector2
src/rocket_sim/physics.py      force equations and semi-implicit Euler segment update
src/rocket_sim/simulation.py   state, lifecycle, fixed-step clock, events, and history
src/rocket_sim/rendering.py    world-to-screen transform, drawing, and telemetry
src/rocket_sim/app.py          Pygame loop and controls
src/rocket_sim/__main__.py     python -m rocket_sim entry point
```

The physics modules do not import Pygame. Rendering reads immutable state samples and cannot change simulation results.

## Numerical and event semantics

- Each constant-force segment uses semi-implicit Euler: velocity is updated before position.
- The display loop supplies elapsed wall time to a compensated accumulator; only complete fixed `physics_dt_s` steps advance the model, with no epsilon-created time.
- Paused or pre-launch wall time is not accumulated, and reset clears accumulator residue.
- A step spanning burnout is divided at the exact half-open burn boundary, preventing excess or missing thrust impulse.
- Acceleration telemetry is the instantaneous acceleration at the resulting state time; at exact burnout it therefore shows coast acceleration.
- Ground return is detected only after liftoff. The first descending discrete segment that crosses `y = 0` is linearly interpolated to the ground, then the flight becomes terminal. This is deterministic interpolation of the discrete numerical path, not an exact impact solve. A terminal sample represents the instant of impact, so thrust and instantaneous acceleration still reflect that time even when impact precedes burnout.

## Validation status

The headless test suite covers configuration validation, force signs and components, burn-boundary predicates, constant mass, Euler ordering, analytical gravity/powered/piecewise motion, non-aligned burnout splitting, limiting cases, first-order timestep convergence, reset determinism, interpolated ground return, 30/60/144 FPS partition independence, coordinate conversion, rendering non-mutation, controls, package import, and a bounded dummy-display application smoke test.

Analytical expected values are calculated independently in tests rather than through production force or integration helpers.

## Current limits

There is no drag, variable mass, real motor curve, atmosphere, wind, recovery, collision dynamics, rotation, stability, guidance, control, experiment export, calibration, or uncertainty model. The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction.

The next milestone remains out of scope for Prompt 02.
