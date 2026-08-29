# Validation and Testing

## Evidence standard

RocketSim validates simple cases against independently calculated answers before relying on integrated flight behavior. Expected force values and analytical trajectories in tests are calculated directly from literal parameters and equations, not by calling the production drag or force-breakdown helpers. A finer production run is not used as the sole nonlinear oracle.

The complete suite runs headlessly with:

```bash
conda run -n rocketsim python -m pytest
```

## Prompt 02 regression baseline

Prompt 02 gravity/thrust tests explicitly set air density to zero when their references assume constant acceleration. They retain force signs, the half-open burn predicate, semi-implicit update ordering, exact non-aligned burnout split, constant-mass behavior, analytical gravity/powered/piecewise motion, the known constant-acceleration position-error identity, ground interpolation, reset, strict accumulator semantics, and display-FPS independence.

An additional integrated analytical case independently verifies that each of `rho = 0`, `Cd = 0`, and `A = 0` produces the same literal Prompt 02 result. There is no separate no-drag implementation.

## Aerodynamic configuration and force algebra

The suite verifies:

- finite, non-negative density, `Cd`, and area with exact zero accepted;
- negative, NaN, and infinite aerodynamic inputs rejected;
- exactly zero drag at zero velocity;
- exactly zero drag when density, `Cd`, or area is zero;
- cardinal and all four diagonal velocity quadrants;
- drag reversal when velocity reverses;
- strict negative `F_drag dot v` for positive parameters and nonzero speed;
- fourfold magnitude when speed doubles;
- scalar magnitude `0.5 rho Cd A speed^2`; and
- a literal combined thrust/gravity/drag/net-force and acceleration oracle.

For the independent vector oracle `rho=2`, `Cd=0.5`, `A=0.25`, and `v=(3,4) m/s`, the expected drag is `(-1.875,-2.5) N` with magnitude `3.125 N`. With `m=2 kg`, `g=3 m/s^2`, and `10 N` thrust along +x, the expected net force is `(8.125,-8.5) N` and acceleration is `(4.0625,-4.25) m/s^2`.

## Drag integration and events

An exact one-step literal case distinguishes the documented numerical ordering:

```text
evaluate drag from v0 = (3,4) m/s
update velocity to (3.40625,3.575) m/s
update position to (1.340625,10.3575) m
```

That test then independently recalculates drag, net force, and acceleration from the resulting velocity, proving ordinary recorded-state telemetry is not stale from the segment start.

A deliberately non-aligned active-drag step crosses burnout at `0.5 s` within `dt=1.0 s`. Its powered substep reaches `vx=2.75 m/s`; the coast substep recomputes drag as `-3.78125 N` from that burnout velocity and ends at `vx=0.859375 m/s`, `x=1.8046875 m`. The test also requires exactly one burnout sample.

Impact telemetry is independently checked to ensure drag and acceleration are recalculated from the interpolated impact velocity. Ground handling remains interpolation of the discrete numerical segment and is not presented as an exact root solve.

## Analytical vertical quadratic-drag fall

The nonlinear reference uses:

```text
m = 2 kg
g = 8 m/s^2
rho = 2 kg/m^3
Cd = 1
A = 1 m^2
k = 1 kg/m
v_terminal = 4 m/s
y0 = 100 m
vy0 = 0
```

At `t=1 s`, the independent continuous solution is:

```text
vy = -4 tanh(2)
y = 100 - 2 ln(cosh(2))
```

The high starting altitude prevents ground contact. At `dt=0.005 s`, the numerical state is `vy=-3.8598482081 m/s`, `y=97.3355269070 m`; the analytical state is `vy=-3.8561103203 m/s`, `y=97.3499945053 m`.

## Measured timestep convergence

The analytical fall produced these absolute errors:

| `dt` (s) | `|velocity error|` (m/s) | `|altitude error|` (m) |
| ---: | ---: | ---: |
| 0.020 | 0.0148671763 | 0.0578690164 |
| 0.010 | 0.0074621397 | 0.0289350701 |
| 0.005 | 0.0037378878 | 0.0144675983 |

Velocity error ratios as timestep halves are approximately `1.992` and `1.996`; altitude ratios are approximately `2.000` and `2.000`. This measured evidence is consistent with the expected first-order global behavior. It is not a claim of exact constant-acceleration error under active drag.

## Terminal velocity

With the same analytical parameters, tests calculate the expected forces independently:

- at `vy=-4 m/s`, drag is `+16 N`, weight is `-16 N`, and acceleration is zero;
- at `vy=-3 m/s`, net vertical force is `-7 N` and acceleration is downward; and
- at `vy=-5 m/s`, net vertical force is `+9 N` and acceleration is upward.

No terminal-speed clamp exists.

## Integrated lifecycle and time separation

The suite verifies:

- physically coherent drag signs during powered ascent, coast ascent, and descent;
- lower default-flight apogee with drag than in the zero-drag limit;
- constant mass throughout active-drag flight;
- deterministic reset/rerun with velocity-dependent feedback;
- equal state and trajectory for active-drag elapsed time partitioned at 30, 60, and 144 FPS, including an exact burnout boundary;
- paused RIGHT-arrow stepping advances one configured outer step, preserves fractional accumulator residue, remains paused, and retains burnout splitting; and
- RIGHT is inactive before launch, while running, and after landing.

The default `dt=0.01 s` flight is numerically stable for the documented educational constants. The integrator remains explicit with respect to drag and is not claimed stable for arbitrary finite parameters or timesteps.

## Rendering and application

Automated evidence covers:

- no Pygame dependency in configuration, physics, or simulation modules;
- world and force-vector y-axis inversion only at rendering;
- one shared display scale for thrust, gravity, drag, and net force;
- four sentinel production force vectors reaching all four arrow endpoint calculations at that same scale;
- Inspector presence of state, all force values, aerodynamic parameters, and implemented equations;
- distinct Inspector labels for post-liftoff impact and terminal no-liftoff initial states;
- the renderer reading `Simulation.current_forces` while containing no drag helper or drag equation implementation;
- rendering with overlays enabled and disabled without mutating state, history, accumulator, or configuration;
- F and I toggles changing presentation only;
- SPACE, RIGHT, R, and ESC behavior; and
- a bounded SDL dummy-display application run.

The real SDL application launched successfully and remained live until intentionally interrupted. The available desktop-control layer could not attach to the unbundled Python window, so physical keyboard manipulation is not claimed. Separately rendered production frames were visually inspected at powered ascent, coast ascent, descent, and paused-after-single-step states. Arrow directions and numerical labels agreed with the force breakdowns; an initial label-overlap defect was corrected with small rendering-only lateral arrow origins while preserving direction and the common scale. Automated key-event tests cover SPACE, RIGHT, R, F, I, and ESC, and a scripted production-path paused step confirmed one `0.01 s` advance while remaining paused.

Visual inspection supplements these automated checks but is not the scientific oracle.

## Current Prompt 03 suite result

After specialist review corrections, the complete suite reports:

```text
119 passed
```

Focused aerodynamic, analytical, convergence, integration, lifecycle, timing, and rendering groups also pass independently, as does the bounded SDL dummy application smoke test.

## Full validation procedure

Before a completed implementation is committed and pushed:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -m compileall -q src tests
conda run -n rocketsim python -m pytest
conda run -n rocketsim python -c "import rocket_sim"
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy conda run -n rocketsim python -c "from rocket_sim.app import run; raise SystemExit(run(max_frames=2))"
git diff --check
```

Focused aerodynamic, analytical, convergence, integration, lifecycle, accumulator, and rendering tests are also run separately.

## Interpretation limits

The evidence establishes correctness for the documented still-air, constant-property, isotropic point-mass drag approximation and its numerical contract. It does not establish real-world aerodynamic accuracy. Landing values remain timestep-sensitive. Real-flight comparison requires measured vehicle data, calibration kept separate from evaluation, and explicit uncertainty analysis.
