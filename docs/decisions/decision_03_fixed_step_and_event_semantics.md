# Decision 03: Fixed-step integration and event semantics

- Date: 2026-08-27
- Status: accepted
- Related prompt: `docs/prompts/prompt_02_physics.md`
- Supersedes: none

## Decision

Use semi-implicit Euler with a default fixed timestep of `0.01 s`, updating velocity before position. Accumulate unpaused wall time with compensated summation and consume only complete fixed physics steps, retaining fractional residue without dropping or fabricating elapsed time.

Split any fixed step that spans burnout into powered and coast substeps at the exact half-open boundary. Detect a descending return to ground only after liftoff and linearly interpolate the first discrete crossing to `y = 0`; then stop and discard the unused remainder of that physics step.

## Context

The integrator, time-source boundary, and discontinuous events materially determine reproducibility, thrust impulse, displayed phase, and validation tolerances.

## Options considered

- Explicit Euler, semi-implicit Euler, and higher-order methods. Semi-implicit Euler is the required understandable first method; higher-order methods are unnecessary for this milestone.
- Choose thrust once per outer step or split at burnout. Splitting preserves the exact configured powered duration when burnout is not aligned to `dt`.
- End-of-step ground clamp, linear event interpolation, or analytical root solve. Linear interpolation is deterministic and modestly improves event reporting without claiming high-precision collision dynamics.
- Cap accumulator substeps and drop excess time or consume all elapsed time. Consuming all time preserves FPS independence; no arbitrary time-dropping cap is used.

## Rationale

The scheme is simple, deterministic, testable against known first-order position error, and independent of rendering cadence. Exact burnout segmentation avoids a full-step impulse error at the force discontinuity.

## Consequences and tradeoffs

- Constant-acceleration velocity is exact to roundoff, but position has first-order error `0.5 a t dt`.
- Position error should approximately halve with timestep.
- A boundary state at burnout is coast even though the preceding interval was powered.
- Landing is interpolation of the discrete path, not an exact physical impact solution, and remains timestep-sensitive.
- Reset must clear state, trajectory, accumulator, and step count to reproduce a run.
- Zero or representably subthreshold elapsed time never advances a physics step, including for very small positive configured timesteps.

No prior decision is superseded.
