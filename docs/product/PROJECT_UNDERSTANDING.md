# Project Understanding

## Purpose and current milestone

RocketSim is a trustworthy, understandable 2D model-rocket learning simulator rather than an engineering-grade launch predictor. Prompt 03 completes the constant-property quadratic-drag milestone and adds an educational Physics Inspector without adding another physical model.

## Implemented model

The rocket is a constant-mass point in a 2D flat world. Internally, all quantities use SI units, +x points right, +y points upward, and the ground is `y = 0`.

The forces are:

- constant gravity `(0, -m g)`;
- constant thrust `T(cos(theta), sin(theta))` during `0 <= t < burn_time`; and
- quadratic drag `-0.5 rho Cd A |v_air| v_air`.

Air is stationary, so rocket velocity relative to air is numerically equal to ground-frame rocket velocity. Density, drag coefficient, and reference area are fixed for a complete run. The default educational constants are `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`; they are not calibration of a particular rocket. Setting any one of these scalars to zero recovers the validated Prompt 02 no-drag model through the same force path.

## Implemented structure

```text
src/rocket_sim/config.py       immutable Vector2 and validated run constants
src/rocket_sim/physics.py      thrust, gravity, drag, force breakdown, and Euler segment
src/rocket_sim/simulation.py   state, lifecycle, fixed-step clock, events, and history
src/rocket_sim/rendering.py    world transform, force arrows, and Physics Inspector
src/rocket_sim/app.py          Pygame loop and educational controls
src/rocket_sim/__main__.py     python -m rocket_sim entry point
```

The physics modules do not import Pygame. Rendering consumes `Simulation.current_forces`, the same immutable `ForceBreakdown` calculated by the production physics layer. Display scaling and visibility toggles cannot alter physical values or state.

## Numerical and event semantics

- Every numerical segment evaluates thrust, gravity, and drag from its starting time and velocity.
- Semi-implicit Euler then updates velocity before position.
- Drag makes true continuous acceleration velocity-dependent, so Prompt 02's constant-acceleration position-error identity applies only when drag is disabled.
- The display loop supplies elapsed wall time to a compensated accumulator; only complete fixed timesteps advance the model.
- A step spanning burnout is divided at the exact half-open burn boundary. The coast substep recomputes drag from the burnout velocity.
- Recorded acceleration and displayed forces are instantaneous values recalculated from the resulting state's time and velocity, including exact burnout and interpolated impact states.
- Ground return remains deterministic interpolation of the first descending discrete crossing after liftoff, not an exact collision solve.
- A paused RIGHT-arrow command advances exactly one normal configured fixed step, keeps the simulation paused, and preserves fractional accumulator time unless the step lands.

## Educational presentation

The Pygame application shows powered and coast trajectory segments, current phase and burnout status, thrust/gravity/drag/net-force arrows, numerical force components and magnitudes, aerodynamic parameters, and the implemented equations. READY explicitly reports forces as inactive alongside zero stored acceleration; it does not invent a pad normal force.

Controls are SPACE launch/pause/resume, RIGHT single-step while paused, R reset, F force overlay, I Physics Inspector, and ESC exit.

## Validation status

The suite preserves Prompt 02 with explicitly disabled drag and adds independent vector-force oracles, all quadrants, exact zero cases, `v^2` scaling, terminal velocity, a closed-form vertical quadratic-drag fall, measured first-order timestep convergence, active-drag burnout, active-drag reset and FPS independence, paused stepping, rendering isolation, Inspector sourcing, and a bounded SDL dummy application smoke test.

## Current limits

Density, `Cd`, and effective reference area are constant and direction-independent. There is no wind, altitude-varying atmosphere, lift, compressibility, Mach/Reynolds dependence, variable mass, real motor curve, recovery, collision dynamics, rotation, stability, guidance, control, plotting, experiment export, calibration, or uncertainty model. Semi-implicit Euler is explicit with respect to drag and can become unstable for sufficiently large timestep or speed; no artificial clamp conceals that limitation.

The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction. Prompt 04 has not begun.
