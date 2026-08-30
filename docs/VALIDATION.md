# Validation and Testing

## Evidence standard

RocketSim validates simple cases against independently calculated answers before relying on integrated flight behavior. Expected force values, thrust interpolation, impulse, motor metrics, and analytical trajectories in tests are calculated directly from literal parameters and equations, not by calling production curve, drag, or force-breakdown helpers. A finer production run is not used as the sole nonlinear oracle.

The complete suite runs headlessly with:

```bash
conda run -n rocketsim python -m pytest
```

## Prompt 02 regression baseline

Prompt 02 gravity/thrust tests explicitly use a two-sample constant-thrust curve and set air density to zero when their references assume constant acceleration. They retain force signs, the half-open burn predicate, semi-implicit update ordering, exact non-aligned burnout split, constant-mass behavior, analytical gravity/powered/piecewise motion, the known constant-acceleration position-error identity, ground interpolation, reset, strict accumulator semantics, and display-FPS independence.

An additional integrated analytical case independently verifies that each of `rho = 0`, `Cd = 0`, and `A = 0` produces the same literal Prompt 02 result. There is no separate no-drag implementation.

## Sampled propulsion data and metrics

Independent tests cover:

- immutable sample and curve ownership;
- finite, non-negative samples;
- exact first time zero and strictly increasing later times;
- duplicate/decreasing/empty rejection;
- the single-sample `(0,0)` zero-duration limit;
- exact stored values at interior knots;
- literal midpoint interpolation on rising and falling intervals;
- zero thrust before ignition and at/after the half-open burn end;
- a nonzero final stored sample that contributes to the last trapezoid while instantaneous burn-end thrust is zero;
- triangle, rectangle, and multi-segment total impulse;
- partial and cross-segment delivered impulse;
- delivered-impulse monotonicity and interval additivity;
- constant- and zero-thrust factories; and
- independently calculated average and peak thrust.

The launchable synthetic default is:

```text
(0.00 s, 12 N)
(0.05 s, 28 N)
(0.12 s, 24 N)
(0.35 s, 20 N)
(0.70 s, 16 N)
(0.95 s,  8 N)
(1.05 s,  0 N)
```

Literal trapezoid areas are `1.00`, `1.82`, `5.06`, `6.30`, `3.00`, and `0.40 N*s`, giving:

```text
burn duration  1.05 s
total impulse  17.58 N*s
peak thrust    28 N
average thrust 16.742857142857... N
```

The originally proposed zero-at-ignition curve retains independently verified `17.28 N*s` total impulse in an airborne, zero-gravity, zero-drag case. It is not used as the ground-launch default because its first `0.01 s` interval delivers only `0.028 N*s` upward while gravity delivers `0.0981 N*s` downward.

## Exact propulsion impulse and knot boundaries

One-knot and multi-knot tests use literal impulse and position oracles, so a whole-step method that happens to deliver the right final velocity cannot conceal missing internal segmentation. One `0.5 s` outer step crossing `0.1`, `0.2`, and `0.3 s` knots produces exactly one state at each knot, increments the outer step count once, and reaches the independently derived `vx=1.2 m/s`, `x=0.31 m` result.

A constant `4 N` curve ending at the non-grid-aligned time `0.35 s` with `dt=0.2 s` delivers exactly `1.4 N*s`, creates one POWERED-to-COAST transition, reports zero instantaneous thrust at burnout, and ends the second outer step at `vx=1.4 m/s`, `x=0.44 m` with no excess thrust.

With gravity and drag disabled, a literal `10 N*s` curve, `m=2 kg`, and a fixed 30-degree direction produces exactly the independent vector result:

```text
delta_v = 5 (cos(30 deg), sin(30 deg)) m/s
```

This validates motor impulse–momentum without using production total-impulse helpers as the oracle.

With active drag, a literal first segment uses `J_T=0.4 N*s`, independently calculated start drag `(-1.875,-2.5) N`, and gravity `(0,-6) N` to reach `v=(3.10625,3.575) m/s` and `p=(1.310625,10.3575) m`. Resulting-state telemetry then uses instantaneous `T(0.1)=6 N` and drag recalculated from that resulting velocity, proving that segment-average thrust is not displayed as current thrust.

An additional multi-knot active-drag case independently verifies that drag is reevaluated at every curve knot. This is why the configured knot set is documented as part of the numerical mesh.

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

## Sampled-thrust active-drag convergence

A test-local standard-library RK4 oracle independently implements literal sampled thrust, gravity, and quadratic drag. It does not call production interpolation, force, impulse, or stepping helpers. At `t=0.6 s`, its reference is:

```text
position = (2.086955589988, 100.340594347210) m
velocity = (4.360834957988, -0.023157593980) m/s
```

Production errors for the same immutable knot set were:

| `dt` (s) | position-vector error (m) | velocity-vector error (m/s) |
| ---: | ---: | ---: |
| 0.020 | 0.0261762225 | 0.0046348364 |
| 0.010 | 0.0136805265 | 0.0024161277 |
| 0.005 | 0.0068400396 | 0.0012071078 |

Position-error ratios were approximately `1.913` and `2.000`; velocity-error ratios were approximately `1.918` and `2.002`. This is measured evidence consistent with first-order convergence for the selected stable case. Separate zero-gravity/zero-drag runs at all three timesteps reproduce the exact literal motor-impulse velocity to roundoff, isolating the remaining numerical error to position and velocity-dependent drag treatment.

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
- equal state, trajectory, force telemetry, and delivered impulse for the sampled default with active drag partitioned at 30, 60, and 144 FPS through the public accumulator;
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
- Inspector current thrust, motor phase, burn-time progress, duration, peak/average thrust, delivered/total impulse, and time-varying thrust/impulse equations;
- timeline geometry derived from the configured production curve's exact samples and current simulation time;
- timeline cursor clamping that is explicitly labeled after burnout rather than misrepresented as coast simulation time;
- production-curve identity reaching the renderer without a second curve, interpolation, or trapezoid implementation;
- distinct Inspector labels for post-liftoff impact and terminal no-liftoff initial states;
- the renderer reading `Simulation.current_forces` while containing no drag helper or drag equation implementation;
- rendering with overlays enabled and disabled without mutating state, history, accumulator, or configuration;
- F and I toggles changing presentation only;
- SPACE, RIGHT, R, and ESC behavior; and
- a bounded SDL dummy-display application run.

The real SDL application launched successfully and remained live until intentionally interrupted. The available desktop-control layer could not attach to the unbundled Python window, so physical keyboard manipulation is not claimed. Separately rendered production frames were visually inspected at powered ascent, coast ascent, descent, and paused-after-single-step states. Arrow directions and numerical labels agreed with the force breakdowns; an initial label-overlap defect was corrected with small rendering-only lateral arrow origins while preserving direction and the common scale. Automated key-event tests cover SPACE, RIGHT, R, F, I, and ESC, and a scripted production-path paused step confirmed one `0.01 s` advance while remaining paused.

Visual inspection supplements these automated checks but is not the scientific oracle.

## Prompt 03 historical suite result

After specialist review corrections, the complete suite reports:

```text
119 passed
```

Prompt 03 completed with 119 passing tests. Prompt 04 preserves those contracts through constant and zero sampled-curve limiting cases.

## Prompt 04 baseline suite result

After post-implementation specialist corrections, the complete implementation and documentation-development suite reports:

```text
162 passed
```

Focused propulsion, impulse, knot, active-drag, convergence, lifecycle, accumulator, rendering, and Living Course executable-contract groups pass independently.

## Prompt 05 pre-launch laboratory evidence

Prompt 05 adds no equation or integrator change. Its new risk is incorrect or mutable UI-to-configuration wiring, so validation crosses the actual setup, renderer-hitbox, application-event, simulation-ownership, and production-force seams rather than reimplementing the full physics suite in UI tests.

The interface tests establish:

- the default six displayed values equal an exact production `SimulationConfig()`;
- all 12 visible `-`/`+` hitbox centers return the parameter and direction shown by their labels;
- each dispatched hitbox action changes only its literal intended field, while exact motor identity, timestep, initial conditions, and every other field remain unchanged;
- off-grid defaults `rho=1.225` and `g=9.81` step relative to their current values, remain bounded, and return after a `+`/`-` pair without grid snap;
- an accepted whole-config replacement while READY atomically rebuilds state mass, initial position/velocity, singleton trajectory, accumulator, step count, and lifecycle flags;
- the getter-only active configuration rejects complete replacement without any public-state change while powered/running, paused, coast, or landed;
- direct adjustment/Restore actions and renderer hit-testing are both locked outside READY, then unlock after Reset Flight;
- Reset Flight preserves selected config object and motor identities, while Restore Defaults creates the complete exact production default including unexposed timestep, initial vectors, and motor;
- actual Pygame key and mouse events reach the same typed-action dispatcher; primary transitions and Reset semantics agree across input devices; right-click and out-of-panel clicks are no-ops;
- setup strings are generated from the current production config before edit, after edit, after reset, and after restore, with the documented units and precision;
- the fixed-direction preview has an independent `30 deg` screen-endpoint oracle and the draw path passes the exact configured radians;
- draw and hit-testing preserve config identity, state, trajectory, accumulator, step count, running/paused/finished flags; and
- a nondefault selected config reproduces exactly after reset/rerun.

Independent integration oracles prove the labeled parameters reach production physics: a `10 N`, zero-gravity case gives `a=T/m`; `30 deg` splits thrust into `(T sqrt(3)/2, T/2)`; gravity gives `(0,-mg)`; and distinct `rho`, `Cd`, and area edits are checked against a literal `v=(3,4)` quadratic-drag calculation. These tests complement rather than replace the lower-level independent force tests.

The untouched GUI defaults and an explicit `SimulationConfig()` produce identical terminal state, complete trajectory, force telemetry, and step count, preserving the Prompt 04 default flight. The Lesson 10 production runs give:

| experiment | run A | run B |
| --- | --- | --- |
| mass `1.0` vs `1.2 kg` | apogee `8.1031495 m`, landed `3.0579922 s` | apogee `4.6826747 m`, landed `2.4610537 s` |
| `Cd=0.5` vs `1.0`, both `A=0.100 m^2` | apogee `7.1906235 m`, landed `2.9186619 s` | apogee `6.4418044 m`, landed `2.8010351 s` |
| direction `90` vs `60 deg` | terminal `x` approximately zero | terminal `x=18.1176548 m` |

Six production-rendered states were visually inspected in the existing `1200x720` layout: READY default, READY modified, running locked, paused locked, Reset Flight with selection preserved/unlocked, and Restore Defaults. The setup panel, read-only motor/impulse/timestep summary, timeline, direction preview, primary/reset/default actions, and Inspector remained readable without panel overlap. This supplements—rather than replaces—the event, geometry, data-sourcing, and non-mutation tests.

The focused setup/lifecycle/rendering group reports:

```text
82 passed
```

The first complete Prompt 05 implementation suite before specialist post-review reports:

```text
209 passed
```

After targeted learning/test review corrections and selective resolution review, the final complete Prompt 05 suite reports:

```text
211 passed
```

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
Focused propulsion unit, propulsion integration, sampled-thrust convergence, FPS/reset, and timeline/Inspector tests are also run separately.
Focused Prompt 05 setup, simulation lifecycle, application-event, and rendering tests are run separately before the full regression suite.

## Interpretation limits

The evidence establishes correctness for the documented synthetic piecewise-linear propulsion representation and still-air, constant-property, isotropic point-mass drag approximation. Exact curve impulse does not make position, drag impulse, apogee, or impact exact. Ground admission and landing remain timestep-sensitive discrete-event approximations. The default curve is not measured motor data. Real-flight comparison requires measured vehicle/motor data, calibration kept separate from evaluation, and explicit uncertainty analysis.
