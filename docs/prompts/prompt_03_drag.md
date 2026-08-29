# Prompt 03: Validated quadratic aerodynamic drag

- Date: 2026-08-28 (America/Vancouver)
- Scope: physics
- Starting commit: `a75c705f080649b2c49cd12b717421ba1934859a`
- Implementation commit: `c68dfc0b5645b68a3ba5a50d3cd5fe25c0980706`
- Implementation commit message: `Implement validated quadratic aerodynamic drag`
- Target remote: `https://github.com/eugenelin89/rocketsim.git`
- Target branch: `main`
- Push status at record creation: implementation commit exists locally; implementation and prompt-record commits are pending the final non-force push

## Starting repository state

Prompt 03 began on clean `main` tracking `origin/main` at Prompt 02 record commit `a75c705`. The repository contained the validated constant-mass gravity-plus-finite-duration-thrust implementation from Prompt 02, 70 passing tests, Decisions 01–04, and three persistent read-only specialists. No unrelated user work or pre-existing Prompt 03 implementation was present.

The primary development interpreter was Python 3.12.14 at `/Users/eugenelin/.conda/envs/rocketsim/bin/python`, with pip 26.2.1 from the same `rocketsim` Conda environment. The next unused IDs were Prompt 03 and Decision 05.

## Scientific scope and constraints

Prompt 03 introduced exactly one physical effect: quadratic aerodynamic drag in still air with constant air density, constant dimensionless drag coefficient, and constant effective reference area. Constant mass, gravity, thrust, half-open burn timing, fixed-step semi-implicit Euler ordering, exact burnout segmentation, deterministic ground handling, compensated wall-time accumulation, reset determinism, and rendering-FPS independence remain intact.

Explicit non-goals included wind, altitude-varying atmosphere, pressure/temperature, Mach/Reynolds/compressibility effects, lift, orientation-dependent drag, variable mass, real motor curves, rotation, stability, recovery, guidance/control, plots, parameter editors, experiment infrastructure, and Prompt 04 work.

## Persistent specialist infrastructure

Created exactly one new specialist definition:

- `.codex/agents/aerodynamics_reviewer.toml`

It parsed successfully with Python 3.12 `tomllib`, contains the required keys, sets `sandbox_mode = "read-only"` and `model_reasoning_effort = "high"`, and omits `model`. `AGENTS.md` now requires it for drag, aerodynamic force, air-relative velocity, reference area, drag coefficient, air density, and later active aerodynamic models.

The collaboration runtime did not expose a hot-loadable custom `aerodynamics_reviewer` agent type. Decision 04's documented fallback was used honestly: a delegated agent named `aerodynamics_reviewer` was required to read and follow the checked-in TOML and remain read-only. It was successfully invoked for pre- and post-implementation review. The existing physics, numerical, and test specialists were also invoked successfully. No specialist modified repository files.

## Pre-implementation reviews and reconciliation

| Specialist | Principal findings | Reconciled contract |
| --- | --- | --- |
| Aerodynamics | Use `F_drag=-0.5 rho Cd A |v_air| v_air`; still-air `v_air` is numerically ground velocity but conceptually distinct; return exact zero for zero speed or any zero scalar; validate every quadrant, reversal, `v^2`, terminal speed, and the nonlinear fall. | Adopt one vector equation without phase cases; document constant/isotropic assumptions and no calibration claim; choose modest educational defaults. |
| Physics | Sum thrust, gravity, and drag exactly once and divide by constant mass. Drag must remove energy, reverse between ascent/descent, apply through powered/coast flight, and preserve no-drag, burnout, landing, and terminal telemetry semantics. READY needs coherent inactive-force presentation. | Introduce one immutable shared force breakdown; show zero inactive forces in READY; compute landed impact forces from interpolated impact velocity. |
| Numerical | Evaluate drag from segment-start velocity, then update velocity before position. Recompute drag at exact burnout and recompute recorded-state acceleration from the resulting velocity. Preserve accumulator/events and demonstrate first-order nonlinear convergence. Large `k|v|dt/m` may be unstable. | Keep semi-implicit Euler and exact burnout split; share the production force path; document force-frozen segments, stability limits, and the inapplicability of Prompt 02's constant-acceleration error identity under active drag. |
| Tests | Require literal vector/net/step/burnout oracles, analytical `tanh`/`ln(cosh)` fall, terminal restoring signs, each zero-parameter Prompt 02 limit, active-drag reset/FPS, paused stepping, renderer non-mutation, and proof that Inspector/arrows consume production forces. | Preserve old tests with explicit zero drag, add independent nonlinear tests, sentinel presentation tests, and bounded SDL smoke evidence without introducing dependencies. |

The reports agreed on the governing equations and numerical method. The parent reconciled them against the project context, accepted Decisions 02–04, and independent derivation. No reviewer disagreement was silently resolved.

## Aerodynamic model and defaults

Configuration adds finite, non-negative:

```text
air_density_kg_m3 = 1.225
drag_coefficient  = 0.75
reference_area_m2 = 0.01
```

These are constant educational values, not calibration of a specific vehicle. For still air:

```text
v_air = v_rocket_ground
k = 0.5 rho Cd A
F_drag = -k |v_air| v_air
F_net = F_thrust + F_gravity + F_drag
a = F_net / m
```

At zero speed, density, `Cd`, or area, drag is exactly `(0,0)`. For positive parameters and nonzero speed, `F_drag dot v_air = -k |v_air|^3 < 0`. The default 1 kg gravity-only terminal speed is approximately `46.21 m/s`.

## Numerical implementation

Every numerical segment uses:

```text
forces_n = forces(t_n, v_n)
a_n = forces_n.net / m
v_(n+1) = v_n + a_n dt
p_(n+1) = p_n + v_(n+1) dt
```

A crossing step still splits at exact burnout. The coast substep recomputes drag from the updated burnout velocity. Resulting-state, exact-burnout, and interpolated-impact acceleration/forces are recalculated from their own time and velocity. Prompt 02's closed-form constant-acceleration position-error identity remains documented only for the zero-drag limit.

Paused RIGHT-arrow stepping calls the same fixed-step path, increments one outer physics step, retains pause and fractional accumulator time, preserves burnout segmentation, and retains the existing landing behavior.

## Educational Physics Inspector

The Pygame window now has a world panel and Physics Inspector. It displays phase, burnout status, time, position, velocity, speed, acceleration, constant mass, all four force vectors/components/magnitudes, aerodynamic parameters, and only the implemented equations. Thrust, gravity, drag, and net arrows consume `Simulation.current_forces` and use one rendering-only newtons-to-pixels scale.

Powered and coast trajectory segments have distinct colors. READY reports forces inactive rather than inventing a pad-support force. A terminal no-liftoff initial state is distinguished from a post-liftoff impact. Controls are SPACE launch/pause/resume, RIGHT paused single-step, R reset, F force overlay, I Inspector, and ESC exit.

## Implementation summary

Implemented:

- constant aerodynamic configuration and validation;
- exact still-air quadratic vector drag;
- immutable shared `ForceBreakdown`;
- velocity-dependent segment stepping and resulting-state telemetry;
- exact burnout drag reevaluation;
- Prompt 02 zero-drag limiting behavior;
- paused production-path single-step;
- force arrows, Inspector, phase/burnout presentation, and controls;
- independent force, analytical, terminal, convergence, lifecycle, timing, and rendering tests;
- persistent aerodynamic review policy;
- Decision 05 and synchronized physics, architecture, validation, milestone, product, README, and research documentation.

## Files created

- `.codex/agents/aerodynamics_reviewer.toml`
- `docs/decisions/decision_05_quadratic_drag_model.md`
- `tests/test_aerodynamics.py`
- `tests/test_drag_validation.py`

## Files modified

- `AGENTS.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/MILESTONES.md`
- `docs/PHYSICS_MODEL.md`
- `docs/RESEARCH_LOG.md`
- `docs/VALIDATION.md`
- `docs/product/PROJECT_UNDERSTANDING.md`
- `src/rocket_sim/__init__.py`
- `src/rocket_sim/app.py`
- `src/rocket_sim/config.py`
- `src/rocket_sim/physics.py`
- `src/rocket_sim/rendering.py`
- `src/rocket_sim/simulation.py`
- `tests/test_analytical_validation.py`
- `tests/test_config.py`
- `tests/test_convergence.py`
- `tests/test_forces.py`
- `tests/test_integrator.py`
- `tests/test_rendering.py`
- `tests/test_simulation.py`
- `tests/test_time_accumulator.py`

No repository file was deleted.

## Quantitative validation

For the literal vector case `rho=2`, `Cd=0.5`, `A=0.25`, and `v=(3,4) m/s`, drag is `(-1.875,-2.5) N`, magnitude `3.125 N`; doubling speed gives an exact `4.0` magnitude ratio.

For vertical fall from rest with `m=2 kg`, `g=8 m/s^2`, `rho=2`, `Cd=1`, `A=1`, `y0=100 m`, and `v_terminal=4 m/s`, the continuous reference at `t=1 s` is:

```text
vy = -4 tanh(2)
y = 100 - 2 ln(cosh(2))
```

Measured absolute errors were:

| `dt` (s) | velocity error (m/s) | altitude error (m) |
| ---: | ---: | ---: |
| 0.020 | 0.0148671763 | 0.0578690164 |
| 0.010 | 0.0074621397 | 0.0289350701 |
| 0.005 | 0.0037378878 | 0.0144675983 |

Velocity-error ratios were `1.9923` and `1.9964`; altitude ratios were `2.0000` and `2.0000`, consistent with first-order convergence. At downward speeds `3`, `4`, and `5 m/s`, vertical accelerations were `-3.5`, `0.0`, and `+4.5 m/s^2`, confirming terminal equilibrium and restoring signs.

The default active-drag apogee was `10.0714548081 m`, compared with `10.3874140000 m` in the otherwise identical zero-drag limit. Each of zero density, zero `Cd`, and zero area independently reproduced the literal Prompt 02 solution.

## Post-implementation reviews and resolutions

| Specialist | Findings | Resolution and final status |
| --- | --- | --- |
| Aerodynamics | No BLOCKING or IMPORTANT finding. Optional clarity note about the default terminal-speed test. | Test now uses the checked configuration values with an independent terminal formula. Final review: commit-ready. |
| Numerical | No BLOCKING or IMPORTANT finding. Verified segment-start evaluation, burnout recomputation, resulting/impact acceleration, convergence, stability claims, FPS, reset, and paused stepping. | No correction required. Final review: commit-ready. |
| Physics | IMPORTANT: every `LANDED` Inspector state was labeled as impact even when an unsupported ground start never lifted off. | Renderer now labels `has_lifted_off=False` as `NO LIFTOFF / terminal initial state`; physics and architecture docs were qualified; regression added. Final resolution review: no remaining BLOCKING/IMPORTANT findings. |
| Tests | IMPORTANT: ordinary resulting-state acceleration lacked an independent new-velocity oracle. IMPORTANT: requesting `current_forces` did not prove all four arrows consumed those vectors at the common scale. Optional: assert exact thrust/still-air equations and aerodynamic values. | Exact one-step test independently calculates resulting drag/net/acceleration. Sentinel spy requires thrust/gravity/drag/net endpoint calls at one scale. Exact UI assertions added. Final resolution review: no remaining BLOCKING/IMPORTANT findings. |

The test specialist's first final-resolution retry was interrupted solely by the Codex usage limit. On the material resume instruction, the same checked-in fixes were audited without changes; the resumed specialist reran focused/full validation and explicitly reported commit-ready status.

The parent visual audit also found overlapping collinear force labels. Small rendering-only lateral origins and opposing label offsets corrected readability without changing physical direction, magnitude, or the common scale.

## Deferred or rejected findings

No BLOCKING or IMPORTANT finding was rejected or deferred.

Optional additions omitted because they were unnecessary or outside the minimal Prompt 03 contract include a coast mechanical-energy regression, fixed-seed randomized dot-product cases, an optional velocity arrow, graphs, parameter editors, and generalized force/atmosphere frameworks. Extreme finite inputs can overflow calculated force; this is documented as outside physically meaningful model use rather than concealed with arbitrary clamps.

## Validation performed

Environment and infrastructure:

```text
Python 3.12.14
/Users/eugenelin/.conda/envs/rocketsim/bin/python
pip 26.2.1 from /Users/eugenelin/.conda/envs/rocketsim/lib/python3.12/site-packages/pip (python 3.12)
tomllib: four read-only high-effort agent definitions, no model overrides
```

Build, import, and complete suite:

```text
conda run -n rocketsim python -m compileall -q src tests
passed

conda run -n rocketsim python -m pytest
119 passed in 0.43s

conda run -n rocketsim python -c "import rocket_sim"
passed
```

Focused evidence:

```text
tests/test_aerodynamics.py + tests/test_drag_validation.py
25 passed

terminal-velocity selection
2 passed

quadratic-drag convergence selection
1 passed

zero-drag / Prompt 02 analytical, Euler, and burnout selection
14 passed

FPS / reset / accumulator / paused-step selection
9 passed
```

Application and repository:

```text
bounded SDL dummy application, 3 frames
passed

git diff --check
passed

git diff --cached --check
passed
```

The real SDL application launched and remained live until intentionally interrupted. The desktop-control layer could not attach to the unbundled Python window, so physical keyboard manipulation is not claimed. Production-rendered frames were visually inspected at powered ascent, coast ascent, descent, and paused-after-single-step. The values and arrows agreed qualitatively and quantitatively with the force breakdown. Automated key-event tests cover all controls.

No formatter, linter, or type checker was run because none is configured and no dependency was added solely for generic tooling. No real-flight comparison was performed because the model is intentionally uncalibrated and this milestone requires analytical, limiting, and numerical validation rather than engineering prediction.

## Final repository audit before implementation commit

The staged implementation contained exactly four persistent specialists, one new Decision 05, scoped drag/core/UI/test/documentation changes, and no prompt record. Audit found no credentials, environment files, generated artifacts, future physics, wind, variable atmosphere, variable mass, real motor curves, rotation, stability, recovery, guidance/control, plotting, experiment infrastructure, or Prompt 04 work. The staged diff contained 26 files, 1,627 insertions, and 219 deletions, and passed `git diff --cached --check`.

## Original Prompt 03 — verbatim

~~~~~~text
Work in:

```text
/Users/eugenelin/dev/cwsf2027/rocketsim
```

Canonical repository:

```text
https://github.com/eugenelin89/rocketsim.git
```

This is **Prompt 03**.

Prompt 02 completed the first scientifically validated 2D constant-mass RocketSim model with:

* constant gravity
* finite-duration constant thrust
* fixed world-frame thrust direction
* fixed-timestep semi-implicit Euler integration
* exact burnout splitting
* deterministic ground-return handling
* Pygame-independent physics
* Pygame visualization
* analytical validation
* timestep-convergence validation
* FPS independence
* persistent specialist review infrastructure

Prompt 03 should introduce exactly one new physical effect:

> **Quadratic aerodynamic drag in still air with constant air density, constant drag coefficient, and constant reference area.**

Prompt 03 should also improve the Pygame presentation into an educational **Physics Inspector** that lets the user see the physical quantities and forces acting on the rocket.

The educational UI must expose the physics already being calculated. It must not introduce new physical models.

Do not start variable mass, real motor curves, atmospheric variation, wind, rotation, stability, recovery, guidance, or control.

The intended scientific progression is:

```text
Prompt 02
gravity + thrust
        ↓
Prompt 03
gravity + thrust + quadratic drag
        ↓
independent analytical / limiting validation
        ↓
educational force visualization
```

The parent Codex agent remains the sole primary implementer and integrator.

Specialist agents remain read-only reviewers.

---

# 1. Required reading and repository inspection

Before editing:

1. Read `AGENTS.md` completely.
2. Read `Pygame_Rocket_Simulator_Project_Context.md`.
3. Read `docs/product/PROJECT_UNDERSTANDING.md`.
4. Read:

   * `docs/PHYSICS_MODEL.md`
   * `docs/ARCHITECTURE.md`
   * `docs/MILESTONES.md`
   * `docs/VALIDATION.md`
   * `docs/PROJECT_BRIEF.md`
   * `docs/RESEARCH_LOG.md`
5. Read all accepted decisions, especially:

   * Decision 02: constant-thrust state model
   * Decision 03: fixed-step and event semantics
   * Decision 04: specialist review workflow
6. Read Prompt 02's historical record.
7. Inspect all current source modules and tests.
8. Inspect:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 10
```

9. Confirm:

   * working tree is clean
   * current branch is `main`
   * `main` tracks `origin/main`
10. Determine the next unused prompt and decision IDs.

Do not overwrite or absorb unrelated work.

If repository state conflicts materially with this prompt, stop and report the specific conflict.

---

# 2. Python environment

Continue using:

```text
Conda environment: rocketsim
Python: 3.12
```

Verify:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -m pytest
```

Do not create another environment.

Do not create a nested `venv`.

Do not use Conda `base`, Homebrew Python, system Python, or user-global Python.

Do not add NumPy, SciPy, pandas, matplotlib, or another dependency manager.

Python standard library, Pygame, and pytest remain sufficient.

---

# 3. Preserve all Prompt 02 behavior

Prompt 03 must preserve the validated Prompt 02 model.

With aerodynamic drag mathematically reduced to zero, Prompt 03 should reproduce Prompt 02 behavior within the established floating-point semantics.

Do not silently alter:

* coordinate convention
* SI-unit policy
* constant mass
* gravity semantics
* thrust semantics
* half-open burn interval
* exact burnout segmentation
* semi-implicit Euler update ordering
* fixed physics timestep
* wall-time accumulator semantics
* liftoff semantics
* landing semantics
* rendering/physics separation
* reset determinism
* FPS independence

Any necessary change to these established contracts requires explicit justification and specialist review.

---

# 4. Prompt 03 scientific scope

Add only:

* constant air density
* constant drag coefficient
* constant reference area
* still-air relative velocity
* quadratic aerodynamic drag
* drag contribution to net acceleration
* educational display of forces and relevant aerodynamic parameters

Do not add any other physical effect.

---

# 5. Explicit non-goals

Do not implement:

* altitude-dependent air density
* standard atmosphere
* pressure
* temperature
* speed of sound
* Mach number
* Reynolds number
* compressibility
* transonic effects
* variable drag coefficient
* angle-dependent drag coefficient
* lift
* aerodynamic moments
* wind
* gusts
* variable mass
* propellant depletion
* realistic motor curves
* thrust interpolation
* rocket orientation
* rotation
* torque
* moment of inertia
* center of gravity
* center of pressure
* aerodynamic stability
* parachutes
* recovery
* launch-rail physics
* active guidance
* control
* parameter sweeps
* experiment framework
* Monte Carlo analysis
* plotting libraries
* CSV export
* optimization
* machine learning
* multiple rockets
* swarm behavior

Do not create placeholder implementations for these future systems.

---

# 6. Add persistent `aerodynamics_reviewer`

Prompt 03 activates the aerodynamic domain for the first time.

Create:

```text
.codex/agents/aerodynamics_reviewer.toml
```

Do not create other future specialists.

Use the established custom-agent schema.

The definition should be equivalent to:

```toml
name = "aerodynamics_reviewer"
description = "Independently reviews RocketSim aerodynamic-force equations, air-relative velocity, drag direction and magnitude, units, assumptions, and aerodynamic validation."

sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
You are RocketSim's independent aerodynamics reviewer.

You are a reviewer, not an implementation agent.

Do not modify repository files.

Your primary question is:

Does the aerodynamic implementation represent the documented simplified
drag model correctly?

Review:
- air-relative velocity
- still-air assumptions
- quadratic drag equation
- drag direction
- drag magnitude
- zero-speed behavior
- density
- drag coefficient
- reference area
- units and dimensional consistency
- vector formulation
- behavior in every velocity quadrant
- v-squared scaling
- terminal-velocity expectations
- analytical references where available
- limiting cases
- hidden aerodynamic assumptions
- claims of fidelity

For Prompt 03 specifically, the model is constant-density quadratic drag
with constant Cd and reference area in still air.

Do not introduce wind, lift, variable density, variable Cd, Mach effects,
rotation, or stability.

Classify findings as:

BLOCKING
IMPORTANT
OPTIONAL

For each meaningful finding:
- explain the aerodynamic issue
- reference exact files/functions/tests/equations
- state expected behavior
- recommend the smallest scientifically justified correction

Do not modify files.
"""
```

Validate the TOML with Python `tomllib`.

Use the persistent named agent normally if supported.

If the current Codex runtime still cannot hot-load checked-in custom agent types, use the established Decision 04 fallback honestly and record that fact.

---

# 7. Update specialist orchestration policy

Update `AGENTS.md` only as necessary to add `aerodynamics_reviewer`.

It should be required for changes involving:

* drag
* aerodynamic force
* air-relative velocity
* reference area
* drag coefficient
* air density
* later aerodynamic models when they become active

Do not duplicate the full TOML instructions into `AGENTS.md`.

Preserve:

* read-only specialist authority
* parent-agent implementation ownership
* pre-review
* post-review
* blocking-finding resolution
* final validation gate

---

# 8. Prompt 03 specialist pre-review

Before implementing drag, invoke:

* `physics_reviewer`
* `numerical_reviewer`
* `test_reviewer`
* `aerodynamics_reviewer`

They may inspect independently in parallel.

The parent must wait for all four and reconcile their findings before implementation.

---

# 9. Aerodynamics pre-review questions

Ask `aerodynamics_reviewer` to independently derive and verify:

* the correct drag vector equation
* the still-air relative-velocity definition
* zero-speed behavior
* force direction
* dimensional consistency
* expected `v²` scaling
* behavior for positive/negative x and y velocity
* analytical vertical-fall solution where applicable
* terminal velocity
* appropriate limiting cases
* assumptions that must be documented

Do not give implementation code as the source of truth.

---

# 10. Physics pre-review questions

Ask `physics_reviewer` to verify how drag combines with existing gravity and thrust.

Require an explicit check of:

```text
F_net = F_thrust + F_gravity + F_drag
a = F_net / m
```

Review:

* force signs
* coordinate convention
* constant mass
* powered versus coast behavior
* drag during ascent and descent
* terminal behavior
* energy-removing character of drag
* continued correctness of burnout and landing semantics

---

# 11. Numerical pre-review questions

Ask `numerical_reviewer` to examine the consequences of velocity-dependent acceleration.

Prompt 02 used constant acceleration within each segment.

Prompt 03 drag depends on current velocity, so explicitly determine and document the numerical contract for a semi-implicit Euler drag step.

The expected basic semantics are:

```text
evaluate forces from state at beginning of segment
        ↓
compute acceleration
        ↓
v_next = v + a dt
        ↓
p_next = p + v_next dt
```

Burnout splitting remains exact.

Ask the reviewer to examine:

* drag-force evaluation time
* state used for drag calculation
* first-order convergence
* timestep sensitivity
* possible instability at large dt or speed
* event-boundary implications
* analytical-drag test tolerances

Do not change integrator merely to obtain better-looking results unless an explicit accepted decision justifies it.

---

# 12. Test pre-review questions

Ask `test_reviewer` to identify independent evidence for:

* zero-speed drag
* drag direction
* drag `v²` scaling
* zero density
* zero `Cd`
* zero area
* arbitrary velocity quadrants
* Prompt 02 no-drag regression behavior
* vertical free fall with quadratic drag
* terminal velocity
* timestep convergence
* FPS independence
* deterministic reset
* burnout with drag
* rendering isolation
* Physics Inspector correctness

Require expected values to be independent from production helpers.

---

# 13. Reconcile pre-review findings

The parent agent must reconcile all four reports before implementation.

Use:

```text
docs/PHYSICS_MODEL.md
docs/VALIDATION.md
accepted decisions
independent derivation
```

as authoritative sources.

Where a new durable physical or numerical assumption is required, record it appropriately.

Do not silently resolve conflicting reviewer opinions.

---

# 14. Aerodynamic configuration

Extend `SimulationConfig` only as necessary.

Add explicit SI-valued aerodynamic parameters equivalent to:

```text
air_density_kg_m3
drag_coefficient
reference_area_m2
```

Requirements:

```text
air_density_kg_m3 >= 0
drag_coefficient >= 0
reference_area_m2 >= 0
```

All values must be finite.

Allowing zero is important because zero-valued parameters provide exact drag-disabled limiting cases.

Use constant values for the complete flight.

Do not add a general atmosphere object yet.

Do not create a drag-enable boolean if zero-valued parameters already cleanly disable drag.

---

# 15. Default aerodynamic parameters

Choose simple, documented educational defaults.

The default should:

* keep the existing 1 kg constant-mass rocket understandable;
* produce visible but not overwhelming drag;
* remain numerically stable at `dt=0.01 s`;
* not be presented as calibration of a specific real rocket.

A sea-level-like constant density such as:

```text
rho = 1.225 kg/m³
```

is reasonable.

Choose and document a simple constant `Cd` and reference area.

Do not claim these defaults match an actual vehicle unless supported by measured data.

---

# 16. Air-relative velocity

Prompt 03 assumes still air.

Therefore:

```text
v_air = v_rocket
```

where `v_air` means rocket velocity relative to the surrounding air.

Document this carefully because future wind will change the relationship.

Do not introduce a wind vector yet.

Do not name ground-relative velocity and air-relative velocity interchangeably in scientific documentation.

For this milestone they are numerically equal because the air is stationary.

---

# 17. Quadratic drag equation

Define:

```text
k = 0.5 rho Cd A
```

For air-relative velocity vector:

```text
v = (vx, vy)
speed = |v|
```

use the vector drag equation:

```text
F_drag = -0.5 rho Cd A |v| v
```

equivalently:

```text
F_drag = -k |v| v
```

This ensures:

```text
|F_drag| = 0.5 rho Cd A speed²
```

and drag points opposite velocity.

At:

```text
speed = 0
```

drag must be exactly:

```text
(0, 0)
```

Do not normalize a zero vector.

---

# 18. Drag physical properties

The implementation must naturally satisfy:

```text
F_drag · v <= 0
```

for all velocities.

For nonzero velocity:

```text
F_drag · v < 0
```

when:

```text
rho > 0
Cd > 0
A > 0
```

Doubling speed with unchanged direction should multiply drag magnitude by approximately four.

Reversing velocity should reverse drag direction.

Do not hard-code special direction cases.

---

# 19. Net force

The complete Prompt 03 model becomes:

```text
F_net =
    F_thrust
    + F_gravity
    + F_drag
```

and:

```text
a = F_net / m
```

Constant mass remains unchanged.

Drag applies during:

* powered flight
* coast ascent
* coast descent

provided velocity relative to air is nonzero.

There is no aerodynamic force after the simulation has reached its terminal landed state because no further motion is integrated.

---

# 20. Prompt 02 limiting equivalence

If any of:

```text
rho = 0
Cd = 0
A = 0
```

then:

```text
F_drag = 0
```

and the model should reduce naturally to Prompt 02 behavior.

Create regression evidence demonstrating this.

Do not maintain a separate no-drag physics implementation.

---

# 21. Numerical integration with drag

Preserve fixed-step semi-implicit Euler.

For each constant-model segment, evaluate aerodynamic acceleration from the segment's starting velocity.

Conceptually:

```text
F_drag(v_n)
F_net(v_n)
a_n = F_net(v_n) / m

v_(n+1) = v_n + a_n dt
p_(n+1) = p_n + v_(n+1) dt
```

Document that acceleration is no longer constant over the true continuous interval because drag depends on velocity.

Therefore the Prompt 02 constant-acceleration closed-form position-error identity does not apply generally when drag is active.

This is an important scientific distinction.

Do not continue claiming exact constant-acceleration velocity behavior when drag is enabled.

---

# 22. Burnout remains an exact event

If a fixed timestep crosses burnout:

```text
powered substep
→ exact burnout
→ coast substep
```

must remain intact.

Drag should be recomputed for each segment from that segment's starting velocity.

Do not apply one drag calculation across both powered and coast subsegments if the velocity changed at burnout.

---

# 23. Vertical quadratic-drag analytical reference

Use a high-value analytical test for a rocket falling vertically from rest in still air with:

```text
thrust = 0
constant mass
constant gravity
constant rho
constant Cd
constant A
```

Define:

```text
k = 0.5 rho Cd A
```

and terminal downward speed magnitude:

```text
v_terminal = sqrt(m g / k)
```

equivalently:

```text
v_terminal = sqrt(2 m g / (rho Cd A))
```

For downward fall from rest, with +y upward:

```text
v_y(t) =
    -v_terminal * tanh(g t / v_terminal)
```

and:

```text
y(t) =
    y0
    - (v_terminal² / g)
      * ln(cosh(g t / v_terminal))
```

Use a sufficiently high starting altitude and validation interval so ground contact does not interfere.

Derive expected values independently in tests.

Use this as a principal scientific reference for the nonlinear drag implementation.

---

# 24. Terminal-velocity validation

For vertical downward velocity:

```text
v = (0, -v_terminal)
```

in coast with no thrust, net vertical acceleration should be approximately zero.

Also validate:

```text
|v| < v_terminal
```

during downward fall produces downward acceleration, while:

```text
|v| > v_terminal
```

produces upward net acceleration.

Use independent equations for expected values.

---

# 25. Required aerodynamic unit tests

At minimum test:

1. drag is exactly zero at zero speed;
2. drag is zero when density is zero;
3. drag is zero when `Cd` is zero;
4. drag is zero when reference area is zero;
5. drag opposes +x velocity;
6. drag opposes -x velocity;
7. drag opposes +y velocity;
8. drag opposes -y velocity;
9. drag opposes diagonal velocities;
10. drag vector dot velocity is non-positive;
11. doubling speed produces 4× drag magnitude;
12. reversing velocity reverses drag force;
13. drag magnitude matches the scalar quadratic equation;
14. net force includes thrust, gravity, and drag exactly once;
15. aerodynamic configuration rejects negative or non-finite values.

Do not build these expected values using the production drag helper.

---

# 26. Required scientific validation

Add independent evidence for:

* analytical vertical quadratic-drag fall
* terminal velocity
* first-order timestep convergence with drag
* zero-drag reduction to Prompt 02
* powered flight with drag
* burnout with drag
* drag direction through ascent and descent
* deterministic reset
* FPS independence

Use at least:

```text
dt = 0.02
dt = 0.01
dt = 0.005
```

for convergence.

The nonlinear drag analytical case should show improved agreement as timestep decreases.

Do not assert a convergence order unsupported by measured evidence; record the observed ratio and compare it with the expected first-order behavior of the chosen method.

---

# 27. Preserve Prompt 02 tests

Do not weaken Prompt 02 validation simply because drag is now enabled by default.

Where tests are specifically validating the Prompt 02 gravity/thrust model, explicitly configure zero drag.

The old scientific baseline remains valuable as a limiting case.

Do not delete rigorous tests just because new physics exists.

---

# 28. Educational UI objective

RocketSim is being used to learn rocketry and physics.

Prompt 03 should therefore make physical causes visible rather than merely showing a trajectory.

Add a **Physics Inspector** presentation layer.

The user should be able to answer questions such as:

```text
What forces are acting on the rocket right now?

Which direction is drag acting?

Why is the rocket slowing down?

How large is thrust relative to gravity?

What happens to thrust after burnout?

Why does drag reverse direction when the rocket begins descending?

How does the net force produce the current acceleration?
```

The UI must display answers derived from the same physics model used by the simulator.

Do not maintain a separate approximation solely for presentation.

---

# 29. Physics Inspector layout

Use a simple educational layout approximately like:

```text
┌───────────────────────────────────────┬──────────────────────────┐
│                                       │ PHYSICS INSPECTOR        │
│             rocket/world              │                          │
│                                       │ Phase                    │
│       force arrows at rocket          │ Time                     │
│                                       │ Position                 │
│       trajectory                      │ Velocity                 │
│                                       │ Speed                    │
│                                       │                          │
│                                       │ FORCES                   │
│                                       │ Thrust                   │
│                                       │ Gravity                  │
│                                       │ Drag                     │
│                                       │ Net                      │
│                                       │                          │
│                                       │ PARAMETERS               │
│                                       │ mass                     │
│                                       │ rho                      │
│                                       │ Cd                       │
│                                       │ reference area           │
│                                       │                          │
│                                       │ EQUATIONS                │
│                                       │ Fg                       │
│                                       │ Ft                       │
│                                       │ Fd                       │
│                                       │ a = ΣF/m                 │
└───────────────────────────────────────┴──────────────────────────┘
```

Exact pixel layout is an implementation choice.

Keep it readable rather than visually elaborate.

---

# 30. Force-vector visualization

Draw force arrows originating at or near the rocket for:

* thrust
* gravity
* drag
* net force

The force vectors displayed must come from the same physical force calculations used by the simulation.

Do not independently reconstruct approximate physics in the renderer.

Each force should have:

* distinguishable visual identity;
* label;
* numerical magnitude in newtons;
* direction corresponding to the physical vector.

Use a single rendering-only force-vector scale so relative force arrow lengths remain meaningful.

If auto-scaling is necessary for visibility, clearly treat that as a display scale rather than physics.

Changing vector scale must not alter simulation results.

---

# 31. Velocity visualization

Optionally display a separate velocity arrow.

If implemented:

* clearly distinguish velocity from force;
* use a separate rendering scale;
* label it in `m/s`;
* never visually imply velocity itself is a force.

This is educationally useful but should remain simple.

---

# 32. Physics Inspector numerical values

Display at least:

```text
phase
simulation time
position
velocity
speed
acceleration
mass

thrust vector / magnitude
gravity vector / magnitude
drag vector / magnitude
net force vector / magnitude

rho
Cd
reference area
```

Use SI units.

Where space allows, show x/y force components as well as magnitude.

Do not add unimplemented quantities such as Mach or dynamic pressure.

---

# 33. Live equation display

Display concise equations in the inspector:

```text
Fg = (0, -mg)

Ft = T(cosθ, sinθ)

Fd = -½ρCdA|v|v

Fnet = Ft + Fg + Fd

a = Fnet / m
```

These equations are educational labels.

They should correspond exactly to `docs/PHYSICS_MODEL.md`.

Do not display equations for unimplemented physics.

---

# 34. Phase visualization

Make the difference between powered and coast flight visually clear.

At minimum:

* show the current phase prominently;
* identify burnout when it occurs.

Where simple, distinguish powered versus coast trajectory segments visually.

Do not create a complex timeline widget yet.

---

# 35. Educational controls

Preserve:

```text
SPACE   launch / pause / resume
R       reset
ESC     quit
```

Add:

```text
RIGHT ARROW   advance exactly one physics timestep while paused
F             show/hide force-vector overlay
I             show/hide Physics Inspector
```

The exact keys may differ only if a clear implementation reason exists.

Display the controls on screen.

---

# 36. Single-step behavior

Single-step is important for learning.

When the simulation is paused during a live flight:

```text
RIGHT ARROW
```

should advance exactly one configured fixed physics timestep and remain paused.

This must:

* use the same production physics path as normal execution;
* preserve burnout segmentation;
* preserve ground-event semantics;
* not alter wall-time accumulator incorrectly;
* remain deterministic.

Do not create a second stepping implementation for educational mode.

Test this behavior.

---

# 37. Force breakdown API

If the current physics layer does not expose force components cleanly enough for both tests and presentation, introduce the smallest Pygame-independent structure justified by the educational UI.

A small immutable structure conceptually like:

```text
ForceBreakdown
    thrust_n
    gravity_n
    drag_n
    net_n
```

may be appropriate.

Do not create a large generalized force-plugin architecture.

The point is to expose the physics already being computed, not invent a framework for future forces.

Ensure:

```text
net = thrust + gravity + drag
```

is validated.

---

# 38. Renderer ownership

The renderer may:

* scale force arrows;
* choose display positions;
* format equations;
* format units;
* hide/show overlays.

The renderer must not:

* calculate a different drag model;
* modify simulation state;
* change timestep;
* change force magnitude;
* change physical parameters;
* affect flight behavior.

Add tests where appropriate to preserve this boundary.

---

# 39. Do not add parameter editing yet

Prompt 03 should display:

```text
rho
Cd
A
```

but should not yet create:

* sliders;
* editable text fields;
* configuration menus;
* presets;
* experiment comparison UI.

Those are strong future educational features, but they would broaden Prompt 03 beyond the single-physics-effect milestone.

---

# 40. Do not add graphs yet

Do not add a plotting subsystem in Prompt 03.

Future educational UI may include:

* altitude vs time
* speed vs time
* thrust/drag/gravity vs time
* acceleration vs time
* energy vs time
* no-drag ghost trajectory comparison

but defer these until separately approved.

Prompt 03 should first establish reliable live force inspection.

---

# 41. Post-implementation specialist review

After implementation and initial tests pass, invoke:

* `physics_reviewer`
* `numerical_reviewer`
* `test_reviewer`
* `aerodynamics_reviewer`

Require each to review the actual resulting code, tests, documentation, and relevant UI-model boundary.

---

# 42. Aerodynamics post-review

Ask directly:

> Does the implementation correctly represent constant-density quadratic drag in still air?

Require review of:

* drag equation
* relative air velocity
* direction
* magnitude
* zero-speed behavior
* `v²` scaling
* reference area
* density
* `Cd`
* terminal speed
* analytical vertical-fall comparison
* limiting cases
* documentation claims

---

# 43. Physics post-review

Ask:

> Does gravity + thrust + drag form a physically coherent Prompt 03 model without altering the validated Prompt 02 contracts?

Require explicit checks of:

* ascent drag
* coast drag
* descent drag
* burnout
* landing
* constant mass
* force addition
* energy-removing direction of drag

---

# 44. Numerical post-review

Ask:

> Does the fixed-step numerical implementation faithfully approximate the new velocity-dependent force model?

Require checks of:

* drag evaluation point
* semi-implicit update order
* burnout segmentation
* convergence
* timestep sensitivity
* analytical-fall agreement
* accumulator independence
* event interaction

---

# 45. Test post-review

Ask:

> Could an incorrect quadratic-drag implementation still pass the current tests?

Require examination of:

* independent force oracles
* analytical falling solution
* terminal velocity
* `v²` scaling
* zero-drag equivalence
* quadrants/directions
* convergence
* FPS independence
* educational UI model sourcing

---

# 46. Resolve findings

For every BLOCKING finding:

1. investigate independently;
2. fix code, tests, or documentation if valid;
3. rerun relevant validation;
4. obtain another review if the fix materially changes reviewed behavior.

Address IMPORTANT findings unless clearly outside Prompt 03.

Do not expand scope merely to satisfy OPTIONAL reviewer suggestions.

Document rejected findings with technical justification.

---

# 47. Documentation updates

Review and update at least:

```text
README.md
AGENTS.md
docs/product/PROJECT_UNDERSTANDING.md
docs/PHYSICS_MODEL.md
docs/ARCHITECTURE.md
docs/VALIDATION.md
docs/MILESTONES.md
```

Update only what actual Prompt 03 implementation requires.

---

# 48. PHYSICS_MODEL requirements

Document:

* still-air assumption
* constant density
* constant `Cd`
* constant reference area
* air-relative velocity
* vector drag equation
* zero-speed behavior
* net-force equation
* drag in ascent/descent
* numerical force-evaluation semantics
* terminal velocity
* analytical vertical-fall reference
* explicit omissions

Do not move scientific truth solely into tests or specialist-agent files.

---

# 49. VALIDATION requirements

Record the actual Prompt 03 evidence.

At minimum document:

* zero-speed drag
* direction/opposition
* `v²` scaling
* zero density / zero `Cd` / zero area
* terminal velocity
* analytical vertical free-fall comparison
* timestep convergence
* zero-drag Prompt 02 regression
* FPS independence
* final pytest result

Do not claim real-world aerodynamic accuracy.

---

# 50. ARCHITECTURE requirements

Document any new concrete ownership such as:

```text
config
    aerodynamic scalar parameters

physics
    drag force + force breakdown

simulation
    force-dependent stepping and lifecycle

rendering
    educational vector visualization / inspector

app
    educational controls
```

Do not introduce speculative aerodynamic frameworks.

---

# 51. Decision records

Create only meaningful durable decisions.

Prompt 03 will likely justify one coherent decision approximately:

```text
decision_05_quadratic_drag_model.md
```

covering:

* still air
* constant density
* constant `Cd`
* constant reference area
* air-relative velocity
* vector drag equation
* force evaluation semantics
* terminal-velocity reference
* known limitations

If the educational Physics Inspector introduces a durable UI/scientific-observability contract worthy of a separate decision, create one only if justified.

Do not produce decision-record clutter.

---

# 52. Research log

A concise scientific research-log entry is appropriate if Prompt 03 produces useful quantitative evidence such as:

> Does measured numerical error against the quadratic-drag analytical fall solution decrease at first order as dt is halved?

Do not turn `RESEARCH_LOG.md` into a Git changelog.

---

# 53. Full automated validation

At minimum run:

```bash
conda run -n rocketsim python --version
conda run -n rocketsim python -c "import sys; print(sys.executable)"
conda run -n rocketsim python -m pip --version
conda run -n rocketsim python -m compileall -q src tests
conda run -n rocketsim python -m pytest
conda run -n rocketsim python -c "import rocket_sim"
git diff --check
```

Also run focused aerodynamic/analytical/convergence tests.

Run a bounded SDL dummy application smoke test.

Run the real application if possible and inspect the Physics Inspector and force vectors.

Do not claim manual controls were tested if the environment cannot actually perform them.

---

# 54. Educational UI manual validation

Where graphical execution is possible, visually inspect at least these states:

### Powered ascent

Expected:

```text
thrust upward
gravity downward
drag opposite upward velocity
net force consistent with values
```

### Coast ascent

Expected:

```text
thrust = 0
gravity downward
drag downward
```

### Descent

Expected:

```text
thrust = 0
gravity downward
drag upward
```

This is one of the most educational Prompt 03 demonstrations.

Verify that the numerical labels match the force arrows qualitatively.

Pause and single-step through at least one state if interactive control is available.

---

# 55. Final specialist gate

Before implementation commit:

```text
physics_reviewer:
    no unresolved BLOCKING findings

numerical_reviewer:
    no unresolved BLOCKING findings

test_reviewer:
    no unresolved BLOCKING findings

aerodynamics_reviewer:
    no unresolved BLOCKING findings
```

IMPORTANT findings may remain only when they are documented and clearly outside Prompt 03 completion requirements.

---

# 56. Final repository audit

Before committing:

```bash
git status
git diff
git diff --check
```

Confirm:

* no environment files
* no caches
* no credentials
* no generated junk
* exactly the intended persistent agents
* no unapproved future physics
* no wind
* no variable atmosphere
* no variable mass
* no real motor curves
* no rotation
* no experiment framework
* no plotting subsystem
* UI uses the same physical model as simulation
* documentation matches implementation
* Prompt 02 behavior remains reproducible when drag is zero

---

# 57. Implementation commit

After specialist review and validation pass, create the implementation commit.

A suitable message:

```text
Implement validated quadratic aerodynamic drag
```

Include:

* drag physics
* aerodynamic configuration
* tests
* Physics Inspector UI
* single-step educational control
* `aerodynamics_reviewer`
* `AGENTS.md` policy update
* relevant documentation
* accepted decision records

Do not include the final Prompt 03 history record yet.

---

# 58. Prompt archive

Create the next prompt record, expected approximately:

```text
docs/prompts/prompt_03_drag.md
```

Use the actual next unused prompt ID.

Preserve this Prompt 03 verbatim.

Also preserve material follow-up instructions.

Include:

* starting repository state
* scientific scope
* aerodynamic assumptions
* specialist infrastructure changes
* pre-review findings
* reconciliation
* implementation summary
* files changed
* analytical validation
* convergence results
* UI/Physics Inspector changes
* post-review findings
* fixes made because of review
* deferred findings
* implementation commit SHA
* exact implementation diff against parent
* push metadata

Commit the prompt record separately.

Suggested message:

```text
Record prompt 03 drag implementation
```

---

# 59. Push

After both commits and a clean working tree:

```bash
git push origin main
```

Do not force push.

Do not rewrite history.

---

# 60. Final verification

Run:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 10
git ls-remote origin refs/heads/main
```

Confirm local and remote state agree.

---

# 61. Definition of done — aerodynamics

Prompt 03 is complete only if:

* quadratic drag exists;
* drag uses still-air relative velocity;
* density is constant;
* `Cd` is constant;
* reference area is constant;
* drag is zero at zero speed;
* drag opposes velocity;
* drag magnitude scales with speed squared;
* zero aerodynamic parameters reduce naturally to Prompt 02;
* net acceleration includes thrust + gravity + drag exactly once;
* no future aerodynamic model was introduced.

---

# 62. Definition of done — numerical/scientific validation

Prompt 03 is complete only if:

* analytical vertical quadratic-drag fall is independently tested;
* terminal velocity is independently tested;
* timestep convergence is demonstrated;
* zero-drag Prompt 02 regression is demonstrated;
* FPS independence remains demonstrated;
* burnout still works with drag;
* deterministic reset remains demonstrated;
* all tests pass;
* no specialist has unresolved BLOCKING findings.

---

# 63. Definition of done — educational UI

Prompt 03 is complete only if:

* force vectors can be displayed;
* thrust is visible;
* gravity is visible;
* drag is visible;
* net force is visible;
* force values are shown numerically;
* aerodynamic parameters are visible;
* relevant equations are visible;
* phase is clearly visible;
* force visualization is sourced from production physics;
* force display does not mutate physics;
* Physics Inspector can be hidden/shown;
* force overlay can be hidden/shown;
* a paused flight can advance one fixed physics timestep;
* educational controls are documented.

---

# 64. Scope after Prompt 03

Do not begin Prompt 04.

Do not assume Prompt 04 automatically introduces variable mass.

After Prompt 03, review what is most educational and scientifically useful before selecting the next physical model.

Likely future directions include:

```text
variable mass
real motor thrust curves
constant wind
altitude-varying atmosphere
educational graphs / experiment comparison
```

but none should be implemented now.

---

# 65. Completion report

When finished, report:

1. starting repository state;
2. persistent specialists used;
3. `aerodynamics_reviewer` creation/invocation status;
4. pre-review findings from all specialists;
5. reconciled aerodynamic model;
6. files created;
7. files modified;
8. aerodynamic configuration parameters;
9. exact drag equation;
10. air-relative velocity semantics;
11. net-force equation;
12. numerical force-evaluation semantics;
13. default aerodynamic values;
14. zero-speed behavior;
15. analytical vertical-fall validation result;
16. terminal-velocity validation result;
17. `v²` scaling result;
18. zero-drag Prompt 02 regression result;
19. timestep-convergence results;
20. FPS-independence result;
21. burnout-with-drag result;
22. deterministic-reset result;
23. Physics Inspector implementation;
24. force-vector implementation;
25. single-step implementation;
26. UI controls;
27. manual/dummy SDL validation;
28. final pytest count and result;
29. post-review findings from all specialists;
30. fixes made because of review;
31. deferred/rejected findings and rationale;
32. decisions created/updated;
33. documentation updated;
34. `git diff --check` result;
35. implementation commit SHA/message;
36. Prompt 03 record path;
37. prompt-record commit SHA/message;
38. remote/branch/upstream;
39. push status;
40. final Git status;
41. scientific limitations;
42. recommended considerations for Prompt 04.

Do not start Prompt 04.
~~~~~~

## Material resume instruction — verbatim

~~~~~~text
Please resume and complete Prompt 03 from the exact current repository state.

The previous execution was interrupted only because the Codex/Work usage limit was reached. Do not restart Prompt 03, undo existing work, discard valid changes, or redo completed work unnecessarily.

First inspect the current Git working tree and determine exactly which Prompt 03 requirements are already complete and which remain outstanding. Continue from the first incomplete required step.

From the prior execution, substantial work was already completed, including:

- `aerodynamics_reviewer` creation and TOML validation
- specialist pre-implementation reviews
- reconciled drag-model contract
- quadratic-drag implementation
- Physics Inspector implementation
- force-vector overlay
- paused single-step behavior
- analytical drag validation
- convergence validation
- FPS-independence validation
- expanded automated test suite
- live rendered-frame inspection
- specialist post-implementation reviews
- several post-review corrections

Immediately before interruption, the parent agent was resolving narrow post-review findings involving:

- distinguishing terminal no-liftoff state from a true post-liftoff impact in the Physics Inspector/documentation
- independently verifying resulting-state acceleration is recomputed from the new velocity
- verifying all four force-arrow endpoint calls use the production force vectors with one common display scale
- low-cost UI assertions for the displayed thrust/still-air equations and exact aerodynamic defaults

Do not assume those final corrections are complete merely because files were edited. Inspect and verify them.

Then complete all remaining Prompt 03 gates, including:

1. finish any unresolved review-driven corrections;
2. run the relevant focused tests;
3. rerun the complete pytest suite;
4. rerun analytical quadratic-drag validation;
5. rerun terminal-velocity validation;
6. rerun timestep-convergence validation;
7. rerun zero-drag Prompt 02 regression validation;
8. rerun FPS-independence and deterministic-reset validation;
9. rerun dummy SDL/application smoke validation;
10. obtain any required final specialist re-review after material fixes;
11. confirm no unresolved BLOCKING findings from:

- `physics_reviewer`
- `numerical_reviewer`
- `test_reviewer`
- `aerodynamics_reviewer`

12. update documentation and Decision 05 if the final fixes require it;
13. perform the complete final diff/repository audit;
14. run `git diff --check`;
15. create the Prompt 03 implementation commit;
16. obtain the implementation commit SHA and exact parent diff;
17. create `docs/prompts/prompt_03_drag.md` using the next actual prompt ID, preserving the full Prompt 03 and material resume instructions verbatim;
18. include specialist findings, validation results, implementation SHA, and implementation diff in the prompt record;
19. commit the Prompt 03 record separately;
20. push both commits to `origin/main` without force;
21. verify local `main`, `origin/main`, and the remote SHA agree;
22. verify the final working tree is clean.

Preserve the existing Prompt 03 scientific scope exactly.

Do not add:

- wind
- altitude-varying atmosphere
- variable mass
- realistic motor curves
- rotation
- stability
- recovery
- guidance/control
- graphing
- experiment infrastructure
- Prompt 04 work

Do not begin Prompt 04.

When complete, provide the full Prompt 03 completion report required by the original Prompt 03, including the final test count, quantitative drag/convergence results, specialist findings and resolutions, UI/Physics Inspector status, implementation commit SHA, prompt-record commit SHA, push verification, and final Git status.
~~~~~~

## Implementation commit patch (exact zero-context diff against parent)

Implementation commit: `c68dfc0b5645b68a3ba5a50d3cd5fe25c0980706`

Parent commit: `a75c705f080649b2c49cd12b717421ba1934859a`

~~~~~~diff
diff --git a/.codex/agents/aerodynamics_reviewer.toml b/.codex/agents/aerodynamics_reviewer.toml
new file mode 100644
index 0000000..50f4236
--- /dev/null
+++ b/.codex/agents/aerodynamics_reviewer.toml
@@ -0,0 +1,58 @@
+name = "aerodynamics_reviewer"
+description = "Independently reviews RocketSim aerodynamic-force equations, air-relative velocity, drag direction and magnitude, units, assumptions, and aerodynamic validation."
+
+sandbox_mode = "read-only"
+model_reasoning_effort = "high"
+
+developer_instructions = """
+You are RocketSim's independent aerodynamics reviewer.
+
+You are a reviewer, not an implementation agent.
+
+Do not modify repository files.
+
+Your primary question is:
+
+Does the aerodynamic implementation represent the documented simplified
+drag model correctly?
+
+Review:
+- air-relative velocity
+- still-air assumptions
+- quadratic drag equation
+- drag direction
+- drag magnitude
+- zero-speed behavior
+- density
+- drag coefficient
+- reference area
+- units and dimensional consistency
+- vector formulation
+- behavior in every velocity quadrant
+- v-squared scaling
+- terminal-velocity expectations
+- analytical references where available
+- limiting cases
+- hidden aerodynamic assumptions
+- claims of fidelity
+
+For Prompt 03 specifically, the model is constant-density quadratic drag
+with constant Cd and reference area in still air.
+
+Do not introduce wind, lift, variable density, variable Cd, Mach effects,
+rotation, or stability.
+
+Classify findings as:
+
+BLOCKING
+IMPORTANT
+OPTIONAL
+
+For each meaningful finding:
+- explain the aerodynamic issue
+- reference exact files/functions/tests/equations
+- state expected behavior
+- recommend the smallest scientifically justified correction
+
+Do not modify files.
+"""
diff --git a/AGENTS.md b/AGENTS.md
index e4f1349..29d330f 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -39,0 +40,4 @@ Invoke before completing any milestone that changes simulation behavior.
+### `aerodynamics_reviewer`
+
+Invoke for changes involving drag, aerodynamic force, air-relative velocity, reference area, drag coefficient, air density, or later aerodynamic models when those domains become active.
+
diff --git a/README.md b/README.md
index a4135a0..57997c7 100644
--- a/README.md
+++ b/README.md
@@ -3 +3 @@
-RocketSim is a scientifically inspectable 2D model-rocket flight simulator built with Python and Pygame. Its first flight milestone implements a constant-mass point rocket under constant gravity and finite-duration constant thrust, with a fixed physics timestep that is independent of display FPS.
+RocketSim is a scientifically inspectable 2D model-rocket flight simulator built with Python and Pygame. Its current milestone models a constant-mass point rocket under gravity, finite-duration constant thrust, and constant-property quadratic aerodynamic drag in still air. A fixed physics timestep remains independent of display FPS.
@@ -7 +7 @@ RocketSim is a scientifically inspectable 2D model-rocket flight simulator built
-Milestone 1 is implemented. The runnable application displays the flight trajectory and live telemetry while a Pygame-independent physics core owns forces, integration, event transitions, and history.
+Milestone 2 is implemented. The runnable application includes a Physics Inspector and force-vector overlay while a Pygame-independent physics core remains the sole owner of force calculations, integration, event transitions, and history.
@@ -13,0 +14,2 @@ Implemented physics:
+- constant density, drag coefficient, and reference area
+- still-air quadratic drag `F_drag = -0.5 rho Cd A |v_air| v_air`
@@ -18 +20 @@ Implemented physics:
-Drag, variable mass, sampled thrust curves, wind, atmosphere, recovery, rotation, stability, guidance, and control are not implemented.
+The aerodynamic defaults are educational constants, not calibration of a real vehicle: `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`. Variable mass, sampled thrust curves, wind, atmosphere variation, lift, recovery, rotation, stability, guidance, and control are not implemented.
@@ -40,0 +43 @@ Controls:
+- `RIGHT ARROW`: advance exactly one physics timestep while paused
@@ -41,0 +45,2 @@ Controls:
+- `F`: show or hide force vectors
+- `I`: show or hide the Physics Inspector
@@ -44 +49 @@ Controls:
-Telemetry shows phase, simulation time, position, velocity, speed, acceleration, mass, and current thrust. The default vertical configuration uses a `1 kg` rocket, `20 N` thrust, a `1 s` burn, and `9.81 m/s²` gravity, so thrust exceeds weight during launch.
+The inspector shows phase, burnout status, state, acceleration, mass, all force vectors and magnitudes, the aerodynamic constants, and the implemented equations. Thrust, gravity, drag, and net-force arrows use the same rendering-only scale and are sourced from the force breakdown used by the simulator. The default vertical configuration uses a `1 kg` rocket, `20 N` thrust, a `1 s` burn, and `9.81 m/s^2` gravity, so thrust exceeds weight during launch.
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 93b4be8..4170e9f 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -17 +17 @@ fixed-step accumulator -> simulation.py lifecycle/events
-physics.py forces + semi-implicit Euler
+physics.py force breakdown + semi-implicit Euler
@@ -34 +34 @@ rendering.py world transform + drawing + telemetry
-- SI-valued defaults and initial conditions
+- SI-valued defaults, initial conditions, and constant aerodynamic scalars
@@ -38 +38 @@ rendering.py world transform + drawing + telemetry
-- gravitational and thrust force equations
+- gravitational, thrust, and constant-property quadratic-drag equations
@@ -40,2 +40,3 @@ rendering.py world transform + drawing + telemetry
-- net acceleration
-- one constant-acceleration semi-implicit Euler segment
+- immutable thrust/gravity/drag/net `ForceBreakdown`
+- net acceleration from the force sum
+- one force-frozen semi-implicit Euler segment
@@ -50 +51,3 @@ It does not own wall time, phases, events, or drawing.
-- exact burnout split and deterministic ground-crossing handling
+- paused exact single-step through the normal fixed-step path
+- exact burnout split with drag reevaluation
+- deterministic ground-crossing handling
@@ -57,2 +60,4 @@ Configuration is the source of constant mass. Every recorded state repeats that
-- world metres to screen pixels
-- ground, trajectory, rocket, and telemetry drawing
+- world metres and force vectors to screen pixels
+- powered/coast trajectory colors, rocket, and educational status drawing
+- force-vector overlay with one rendering-only newtons-to-pixels scale
+- Physics Inspector formatting for state, forces, parameters, and equations
@@ -65 +70 @@ Configuration is the source of constant mass. Every recorded state repeats that
-- `SPACE`, `R`, and `ESC` controls
+- `SPACE`, `RIGHT`, `R`, `F`, `I`, and `ESC` controls
@@ -67,0 +73,6 @@ Configuration is the source of constant mass. Every recorded state repeats that
+## Shared force-observability contract
+
+`physics.force_breakdown_n(config, time, velocity)` is the single production source for thrust, gravity, drag, and net force. The simulation uses its net vector for acceleration and exposes the current breakdown for presentation. The renderer receives those vectors and may only scale, label, color, or hide them; it does not import the drag helper or reproduce the aerodynamic equation.
+
+READY is a lifecycle state rather than a solved pad-contact equilibrium. The simulation therefore exposes an all-zero inactive breakdown while READY so the inspector's zero acceleration and force sum remain coherent without an invented support force. Powered, coast, and terminal states expose their appropriate instantaneous force breakdown; terminal presentation distinguishes a post-liftoff impact from a no-liftoff initial state.
+
@@ -76 +87 @@ No absolute comparison tolerance creates simulation time. Burnout is handled by
-The flight phases are ready, powered, coast, and landed. Pause is an application lifecycle state layered over the physical powered/coast phase. State acceleration describes the instantaneous force model at the state's resulting time, so a state exactly at burnout is coast even if the preceding interval was powered.
+The flight phases are ready, powered, coast, and landed. Pause is an application lifecycle state layered over the physical powered/coast phase. State acceleration describes the instantaneous force model at the state's resulting time and velocity, so a state exactly at burnout is coast even if the preceding interval was powered. A step split at burnout calls the force path independently for the powered and coast segments, so the latter uses updated burnout velocity for drag.
@@ -78 +89 @@ The flight phases are ready, powered, coast, and landed. Pause is an application
-Burnout and landing are handled inside the simulation boundary. A terminal state is the instant of impact, so pre-burn impact retains time-consistent thrust and acceleration telemetry. Rendering infers no transitions and performs no force calculations.
+Burnout and landing are handled inside the simulation boundary. A post-liftoff terminal landed state is the instant of impact, so pre-burn impact retains time-consistent thrust, drag, and acceleration telemetry. A terminal state with `has_lifted_off=False` instead records an unsupported no-liftoff initial condition and is presented distinctly from impact. Rendering infers no transitions and performs no physical force calculations.
@@ -82 +93 @@ Burnout and landing are handled inside the simulation boundary. A terminal state
-Prompt 02 deliberately does not introduce motor interfaces, atmosphere interfaces, data loaders, experiment frameworks, plugins, databases, ECS, networking, or abstractions for unimplemented milestones. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
+Prompt 03 deliberately adds no atmosphere or aerodynamic plugin interface: three constant scalars and one vector equation are sufficient. It does not introduce motor interfaces, wind, lift, data loaders, experiment frameworks, plots, plugins, databases, ECS, networking, or abstractions for unimplemented milestones. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
diff --git a/docs/MILESTONES.md b/docs/MILESTONES.md
index edc8c79..9e56157 100644
--- a/docs/MILESTONES.md
+++ b/docs/MILESTONES.md
@@ -50 +50 @@ Validation:
-Status: not started. It is outside Prompt 02.
+Status: complete in Prompt 03.
@@ -52 +52,24 @@ Status: not started. It is outside Prompt 02.
-When separately approved, this milestone may add quadratic drag with explicit density, drag coefficient, reference area, and air-relative velocity. It will require direction, zero-speed, `v²` scaling, analytical/limiting-case, and timestep-sensitivity evidence. No drag placeholder exists in the current implementation.
+Physics:
+
+- still-air quadratic drag
+- constant density, drag coefficient, and effective reference area
+- exact zero-speed and zero-parameter limiting behavior
+- shared thrust/gravity/drag/net force breakdown
+- drag applied during powered flight, coast ascent, and descent
+
+Features:
+
+- Physics Inspector with SI state, forces, parameters, and equations
+- same-scale thrust, gravity, drag, and net-force arrows
+- powered/coast trajectory distinction
+- force and Inspector visibility toggles
+- exact paused single-step through the normal physics path
+
+Validation:
+
+- independent force magnitude, direction, quadrant, reversal, and `v^2` cases
+- vertical quadratic-drag analytical fall and terminal velocity
+- first-order timestep convergence at `0.02`, `0.01`, and `0.005 s`
+- exact Prompt 02 reduction when density, `Cd`, or area is zero
+- active-drag burnout, reset, and FPS-independence regressions
+- renderer sourcing and non-mutation evidence
diff --git a/docs/PHYSICS_MODEL.md b/docs/PHYSICS_MODEL.md
index 9f0a207..2a7778c 100644
--- a/docs/PHYSICS_MODEL.md
+++ b/docs/PHYSICS_MODEL.md
@@ -3 +3 @@
-## Implemented Milestone 1 model
+## Implemented Milestone 2 model
@@ -5 +5 @@
-RocketSim currently models one constant-mass point rocket in a two-dimensional flat world. It uses SI units internally:
+RocketSim models one constant-mass point rocket in a two-dimensional flat world. It uses SI units internally:
@@ -10 +10 @@ RocketSim currently models one constant-mass point rocket in a two-dimensional f
-- acceleration: metres per second squared (m/s²)
+- acceleration: metres per second squared (m/s^2)
@@ -12,0 +13,2 @@ RocketSim currently models one constant-mass point rocket in a two-dimensional f
+- density: kilograms per cubic metre (kg/m^3)
+- reference area: square metres (m^2)
@@ -19 +21 @@ World +x is horizontal/right, world +y is upward, and the ground is `y = 0`. Scr
-Each recorded state contains simulation time, position, velocity, instantaneous acceleration, constant mass, flight phase, and whether liftoff has occurred. Configuration contains mass, thrust magnitude, burn duration, fixed world launch angle, gravity magnitude, fixed physics timestep, and initial position and velocity.
+Each recorded state contains simulation time, position, velocity, instantaneous acceleration, constant mass, flight phase, and whether liftoff has occurred. Configuration contains mass, thrust magnitude, burn duration, fixed world launch angle, gravity magnitude, constant air density, constant drag coefficient, constant reference area, fixed physics timestep, and initial position and velocity.
@@ -21 +23,27 @@ Each recorded state contains simulation time, position, velocity, instantaneous
-All scalar and vector inputs must be finite. Mass and timestep must be positive. Thrust, burn duration, and gravity magnitude may be zero but not negative. Initial altitude may not be below ground.
+All scalar and vector inputs must be finite. Mass and timestep must be positive. Thrust, burn duration, gravity magnitude, air density, drag coefficient, and reference area may be zero but not negative. Initial altitude may not be below ground.
+
+The default aerodynamic values are educational constants:
+
+```text
+air density      1.225 kg/m^3
+drag coefficient 0.75
+reference area   0.01 m^2
+```
+
+They provide visible but modest drag for the default 1 kg scenario. They are not measurements or calibration of a specific vehicle.
+
+## Air-relative velocity
+
+Prompt 03 assumes still air. In general, rocket velocity relative to the air is conceptually:
+
+```text
+v_air = v_rocket_ground - v_air_ground
+```
+
+The modeled air is stationary, so `v_air_ground = (0, 0)` and therefore:
+
+```text
+v_air = v_rocket_ground
+```
+
+These are numerically equal in this milestone but are not interchangeable physical concepts. No wind vector exists in the implementation.
@@ -25 +53 @@ All scalar and vector inputs must be finite. Mass and timestep must be positive.
-For constant mass `m > 0`, gravity magnitude `g >= 0`, thrust magnitude `T >= 0`, fixed launch angle `theta`, and burn duration `t_b >= 0`:
+For constant mass `m > 0`, gravity magnitude `g >= 0`, thrust magnitude `T >= 0`, fixed angle `theta`, burnout time `t_b >= 0`, air density `rho >= 0`, drag coefficient `Cd >= 0`, reference area `A >= 0`, and air-relative velocity vector `v_air`:
@@ -31 +59 @@ F_g = (0, -m g)
-Thrust uses an exact half-open time interval:
+Thrust uses the exact half-open time interval:
@@ -38 +66 @@ F_T(t) = (0, 0)                    otherwise
-Negative time never produces thrust. Net acceleration is:
+Define:
@@ -41 +69,2 @@ Negative time never produces thrust. Net acceleration is:
-a(t) = (F_T(t) + F_g) / m
+k = 0.5 rho Cd A
+speed = |v_air|
@@ -44 +73 @@ a(t) = (F_T(t) + F_g) / m
-Therefore the powered and coast accelerations are:
+Quadratic drag is:
@@ -47,2 +76 @@ Therefore the powered and coast accelerations are:
-a_power = (T cos(theta) / m, T sin(theta) / m - g)
-a_coast = (0, -g)
+F_drag = -k |v_air| v_air
@@ -51 +79 @@ a_coast = (0, -g)
-Mass does not change at ignition, burnout, coast, or landing.
+and has scalar magnitude:
@@ -53 +81,3 @@ Mass does not change at ignition, burnout, coast, or landing.
-## Numerical integration
+```text
+|F_drag| = 0.5 rho Cd A speed^2
+```
@@ -55 +85,3 @@ Mass does not change at ignition, burnout, coast, or landing.
-The default fixed physics timestep is `dt = 0.01 s`. Every interval over which acceleration is constant uses semi-implicit Euler in this exact order:
+At exactly zero air-relative speed, drag is exactly `(0, 0)`; no zero vector is normalized. If `rho`, `Cd`, or `A` is zero, drag is also exactly zero and the same force path reduces naturally to Prompt 02.
+
+The vector equation works in every quadrant without phase-specific direction cases. For positive aerodynamic parameters and nonzero velocity:
@@ -58,2 +90 @@ The default fixed physics timestep is `dt = 0.01 s`. Every interval over which a
-v_next = v_current + a_current dt
-p_next = p_current + v_next dt
+F_drag dot v_air = -k |v_air|^3 < 0
@@ -62 +93,14 @@ p_next = p_current + v_next dt
-If a configured step begins before burnout and ends after it, the simulator performs a powered substep ending exactly at `t_b`, followed by a coast substep for the remaining duration. A step ending exactly at burnout is powered for its entire interval; the resulting state at `t_b` reports coast phase and coast acceleration. A step starting at burnout is entirely coast.
+Drag therefore removes mechanical energy from the rocket's motion: it points downward during ascent and upward during descent. Thrust may still add energy during powered flight.
+
+The complete force and acceleration equations are:
+
+```text
+F_net = F_T + F_g + F_drag
+a = F_net / m
+```
+
+Production code exposes these named vectors in one immutable `ForceBreakdown`. Integration and presentation consume the same calculation. Mass remains constant at ignition, burnout, coast, descent, and landing.
+
+## Numerical integration
+
+The default fixed physics timestep remains `dt = 0.01 s`. For each numerical segment, all forces are evaluated from the segment's starting time and velocity. Semi-implicit Euler then updates velocity before position:
@@ -64 +108,8 @@ If a configured step begins before burnout and ends after it, the simulator perf
-For constant acceleration over `t = N dt`, velocity is exact apart from floating-point roundoff. Semi-implicit position differs from the continuous solution by:
+```text
+F_n = F(t_n, v_n)
+a_n = F_n / m
+v_(n+1) = v_n + a_n dt
+p_(n+1) = p_n + v_(n+1) dt
+```
+
+Drag depends on velocity, so acceleration is not constant over the true continuous interval. The method freezes it only for one numerical segment. Prompt 02's constant-acceleration identity:
@@ -70 +121 @@ p_numerical - p_analytical = 0.5 a t dt
-Position is therefore first-order accurate: its error should approximately halve when `dt` halves.
+continues to apply to the zero-drag constant-acceleration limit, but not generally with active drag. Active-drag accuracy is established by direct comparison with a nonlinear analytical solution and measured timestep convergence.
@@ -72 +123 @@ Position is therefore first-order accurate: its error should approximately halve
-## Continuous analytical references
+If a configured step begins before burnout and ends after it, the simulator performs a powered substep ending exactly at `t_b`, followed by a coast substep for the remainder. The coast substep reevaluates drag from the updated burnout velocity. A state at exact burnout reports zero thrust and force/acceleration evaluated from its burnout velocity.
@@ -74 +125,3 @@ Position is therefore first-order accurate: its error should approximately halve
-For a constant acceleration `a` over duration `t`:
+Recorded acceleration is always the instantaneous force result for the recorded state's time and velocity, not the acceleration frozen over the preceding segment. This also applies to the interpolated impact velocity.
+
+The drag update is explicit with respect to velocity and is not unconditionally stable. A useful drag-only nondimensional step measure is:
@@ -77,2 +130 @@ For a constant acceleration `a` over duration `t`:
-v(t) = v0 + a t
-p(t) = p0 + v0 t + 0.5 a t²
+q = k |v| dt / m
@@ -81 +133,5 @@ p(t) = p0 + v0 t + 0.5 a t²
-For a powered/coast case, evaluate those equations with `a_power` through `t_b` to obtain `p_b` and `v_b`, then with `a_coast` for `tau = t - t_b`:
+Large `q` can cause an unphysical one-step reversal, oscillation, or growth. The default case keeps `q` small; no arbitrary speed or force clamp hides timestep instability.
+
+## Vertical quadratic-drag analytical reference
+
+For vertical fall from rest in still air with positive `m`, `g`, and `k`, define the terminal downward speed magnitude:
@@ -84,2 +140,2 @@ For a powered/coast case, evaluate those equations with `a_power` through `t_b`
-v(t) = v_b + a_coast tau
-p(t) = p_b + v_b tau + 0.5 a_coast tau²
+v_terminal = sqrt(m g / k)
+           = sqrt(2 m g / (rho Cd A))
@@ -88 +144,4 @@ p(t) = p_b + v_b tau + 0.5 a_coast tau²
-These continuous equations are the independent test oracle, with tolerances derived from the known Euler position error.
+With +y upward and initial altitude `y0`:
+
+```text
+v_y(t) = -v_terminal tanh(g t / v_terminal)
@@ -90 +149,4 @@ These continuous equations are the independent test oracle, with tolerances deri
-## Ground boundary
+y(t) = y0
+       - (v_terminal^2 / g)
+         ln(cosh(g t / v_terminal))
+```
@@ -92 +154 @@ These continuous equations are the independent test oracle, with tolerances deri
-Landing cannot trigger merely because the initial position is on the ground. The state first has to attain positive altitude. On the first later descending numerical segment whose endpoints cross from `y > 0` to `y <= 0`, the simulator linearly interpolates time, horizontal position, and velocity between the discrete endpoints, sets altitude to exactly zero, and enters a terminal landed phase. Any remainder of that physics step is discarded.
+At `v_y = -v_terminal`, upward drag balances downward weight and net vertical acceleration is zero. A smaller downward speed produces downward acceleration; a larger downward speed produces upward restoring acceleration. Terminal speed is an equilibrium, not a clamp.
@@ -94 +156 @@ Landing cannot trigger merely because the initial position is on the ground. The
-This is deterministic event interpolation, not an exact root solve. Landing time, range, and impact velocity remain timestep-sensitive and must not be reported as exact.
+## Ground boundary and lifecycle presentation
@@ -96 +158 @@ This is deterministic event interpolation, not an exact root solve. Landing time
-A configuration starting on the ground is accepted only when its initial vertical velocity is non-negative and the endpoint of its first constant-force numerical segment is above ground. A downward initial velocity or a short flight that is too under-resolved to produce a positive first endpoint terminates at the initial ground state without recording negative altitude. Holding or resolving such a rocket on a pad would require an unimplemented contact/normal-force model. Gravity-only and zero-thrust analytical cases therefore start above ground or use a timestep that resolves their upward motion.
+Ground admission, liftoff, and landing retain Prompt 02 semantics. A ground start must have non-negative initial vertical velocity and a positive first drag-inclusive numerical endpoint. After liftoff, the first descending numerical segment that crosses `y = 0` is linearly interpolated in time, horizontal position, and velocity; altitude is set to exactly zero and the state becomes terminal. This is deterministic interpolation of the discrete numerical path, not an exact impact root.
@@ -98 +160 @@ A configuration starting on the ground is accepted only when its initial vertica
-The terminal state represents the instant of impact. If impact occurs before burnout, its instantaneous acceleration and reported thrust still follow the half-open burn model at that impact time; no later motion is integrated.
+A post-liftoff landed state represents the instant of impact. Its displayed drag is evaluated from the nonzero interpolated impact velocity, although no later motion is integrated. An unsupported ground start instead becomes a terminal no-liftoff initial state; it is not labeled as impact, and its force/acceleration snapshot describes the attempted launch. Before launch, READY deliberately reports zero/inactive forces and zero stored acceleration rather than implying thrust is already active or inventing an unmodeled pad-support force.
@@ -107 +169,4 @@ launch angle      pi/2 rad (vertical)
-gravity           9.81 m/s²
+gravity           9.81 m/s^2
+air density       1.225 kg/m^3
+drag coefficient  0.75
+reference area    0.01 m^2
@@ -111 +176 @@ physics timestep  0.01 s
-The continuous powered acceleration is `10.19 m/s²` upward, so this scenario leaves the ground.
+For this educational approximation, the vertical terminal speed under gravity alone is about `46.21 m/s`. The default flight remains capable of liftoff.
@@ -113 +178 @@ The continuous powered acceleration is `10.19 m/s²` upward, so this scenario le
-## Explicit omissions
+## Explicit omissions and interpretation limits
@@ -115 +180 @@ The continuous powered acceleration is `10.19 m/s²` upward, so this scenario le
-The model has no aerodynamic drag, wind, atmospheric variation, propellant depletion, variable mass, sampled thrust curve, attitude change, rotation, recovery device, bounce, structural dynamics, Earth curvature, or Coriolis effect. No empirical game-feel constants or clamps are applied.
+The model has no wind, altitude-varying density, pressure or temperature, lift, orientation-dependent area, variable `Cd`, Mach/Reynolds/compressibility effects, propellant depletion, variable mass, sampled thrust curve, attitude change, rotation, aerodynamic stability, recovery device, bounce, structural dynamics, Earth curvature, or Coriolis effect. Its single direction-independent effective area makes it an isotropic point-mass drag approximation.
@@ -117 +182 @@ The model has no aerodynamic drag, wind, atmospheric variation, propellant deple
-These omissions bound the meaning of results. The 2D point-mass trajectory is a validated learning model, not a calibrated real-flight or engineering-grade prediction.
+No empirical game-feel constants or clamps are applied. The model assumes physically meaningful finite inputs; extreme finite combinations can exceed floating-point range and are not a claim of physical applicability. Results are a validated learning model, not calibrated real-flight or engineering-grade predictions.
diff --git a/docs/RESEARCH_LOG.md b/docs/RESEARCH_LOG.md
index 6fdee0b..145285f 100644
--- a/docs/RESEARCH_LOG.md
+++ b/docs/RESEARCH_LOG.md
@@ -118,0 +119,38 @@ New effects should be implemented only after the current model has been validate
+
+---
+
+## 2026-08-28 — Quadratic-drag timestep convergence
+
+### Question
+
+Does numerical error against the vertical constant-property quadratic-drag solution decrease at first order as the fixed timestep is halved?
+
+### Hypothesis
+
+Because the velocity-dependent force is evaluated at the start of each semi-implicit Euler segment, global velocity and position error should decrease approximately in proportion to `dt` for a stable case.
+
+### Model / assumptions
+
+- Constant mass `2 kg`.
+- Constant gravity `8 m/s^2`.
+- Still air with `rho=2 kg/m^3`, `Cd=1`, and `A=1 m^2`.
+- Vertical fall from rest at `100 m`.
+- No thrust and no ground contact during the `1 s` comparison.
+
+These values give `k=1 kg/m` and terminal speed `4 m/s`. The continuous references are `vy=-4 tanh(2)` and `y=100-2 ln(cosh(2))` at `t=1 s`.
+
+### Method and results
+
+Production simulations at `dt=0.02`, `0.01`, and `0.005 s` were compared directly with the closed form.
+
+| `dt` (s) | velocity error (m/s) | altitude error (m) |
+| ---: | ---: | ---: |
+| 0.020 | 0.0148671763 | 0.0578690164 |
+| 0.010 | 0.0074621397 | 0.0289350701 |
+| 0.005 | 0.0037378878 | 0.0144675983 |
+
+The velocity-error ratios were approximately `1.992` and `1.996`; altitude-error ratios were approximately `2.000` and `2.000`.
+
+### Interpretation and uncertainty
+
+The measured ratios support first-order convergence for this stable nonlinear case. They do not establish stability for arbitrary speed, aerodynamic parameters, or timestep, and they do not validate the constant-property drag approximation against a real rocket. Future physical effects should retain independent analytical or limiting evidence rather than using a fine numerical run as their only oracle.
diff --git a/docs/VALIDATION.md b/docs/VALIDATION.md
index 3816b3c..0036d07 100644
--- a/docs/VALIDATION.md
+++ b/docs/VALIDATION.md
@@ -3 +3 @@
-## Current evidence standard
+## Evidence standard
@@ -5 +5 @@
-RocketSim validates simple cases against independently calculated known answers before relying on integrated flight behavior. Expected analytical values in tests are computed directly from literal parameters and closed-form equations, not by calling production force, phase, or integration helpers.
+RocketSim validates simple cases against independently calculated answers before relying on integrated flight behavior. Expected force values and analytical trajectories in tests are calculated directly from literal parameters and equations, not by calling the production drag or force-breakdown helpers. A finer production run is not used as the sole nonlinear oracle.
@@ -7 +7 @@ RocketSim validates simple cases against independently calculated known answers
-The suite runs headlessly with:
+The complete suite runs headlessly with:
@@ -13 +13 @@ conda run -n rocketsim python -m pytest
-## Implemented checks
+## Prompt 02 regression baseline
@@ -15 +15 @@ conda run -n rocketsim python -m pytest
-### Configuration and force algebra
+Prompt 02 gravity/thrust tests explicitly set air density to zero when their references assume constant acceleration. They retain force signs, the half-open burn predicate, semi-implicit update ordering, exact non-aligned burnout split, constant-mass behavior, analytical gravity/powered/piecewise motion, the known constant-acceleration position-error identity, ground interpolation, reset, strict accumulator semantics, and display-FPS independence.
@@ -17,10 +17 @@ conda run -n rocketsim python -m pytest
-- finite input enforcement
-- positive mass and timestep
-- non-negative thrust, burn duration, and gravity
-- valid zero-valued limiting cases
-- gravitational sign and magnitude
-- thrust components at 0, 90, and 180 degrees
-- net acceleration from force divided by mass
-- thrust immediately before, exactly at, and immediately after burnout
-- negative time producing no thrust
-- constant mass throughout a complete run
+An additional integrated analytical case independently verifies that each of `rho = 0`, `Cd = 0`, and `A = 0` produces the same literal Prompt 02 result. There is no separate no-drag implementation.
@@ -28 +19 @@ conda run -n rocketsim python -m pytest
-Direct identities use approximately `1e-12` absolute tolerance where floating-point trigonometry is involved.
+## Aerodynamic configuration and force algebra
@@ -30 +21 @@ Direct identities use approximately `1e-12` absolute tolerance where floating-po
-### Integration and event boundaries
+The suite verifies:
@@ -32,9 +23,10 @@ Direct identities use approximately `1e-12` absolute tolerance where floating-po
-- one-step ordering that distinguishes semi-implicit from explicit Euler
-- a deliberately non-grid-aligned fixed step that crosses burnout
-- exact powered impulse and coast remainder in the crossing step
-- coast phase and instantaneous coast acceleration at the resulting boundary
-- no false landing at launch
-- deterministic interpolated ground crossing and terminal immutability
-- deterministic no-liftoff behavior for an unsupported ground configuration
-- no negative-altitude history for a downward or under-resolved ground start
-- consistent thrust and acceleration telemetry for an impact before burnout
+- finite, non-negative density, `Cd`, and area with exact zero accepted;
+- negative, NaN, and infinite aerodynamic inputs rejected;
+- exactly zero drag at zero velocity;
+- exactly zero drag when density, `Cd`, or area is zero;
+- cardinal and all four diagonal velocity quadrants;
+- drag reversal when velocity reverses;
+- strict negative `F_drag dot v` for positive parameters and nonzero speed;
+- fourfold magnitude when speed doubles;
+- scalar magnitude `0.5 rho Cd A speed^2`; and
+- a literal combined thrust/gravity/drag/net-force and acceleration oracle.
@@ -42 +34 @@ Direct identities use approximately `1e-12` absolute tolerance where floating-po
-### Independent analytical motion
+For the independent vector oracle `rho=2`, `Cd=0.5`, `A=0.25`, and `v=(3,4) m/s`, the expected drag is `(-1.875,-2.5) N` with magnitude `3.125 N`. With `m=2 kg`, `g=3 m/s^2`, and `10 N` thrust along +x, the expected net force is `(8.125,-8.5) N` and acceleration is `(4.0625,-4.25) m/s^2`.
@@ -44 +36,3 @@ Direct identities use approximately `1e-12` absolute tolerance where floating-po
-The continuous references are:
+## Drag integration and events
+
+An exact one-step literal case distinguishes the documented numerical ordering:
@@ -47,2 +41,3 @@ The continuous references are:
-v(t) = v0 + a t
-p(t) = p0 + v0 t + 0.5 a t²
+evaluate drag from v0 = (3,4) m/s
+update velocity to (3.40625,3.575) m/s
+update position to (1.340625,10.3575) m
@@ -51 +46 @@ p(t) = p0 + v0 t + 0.5 a t²
-They are applied independently to gravity-only, powered constant-acceleration, and piecewise powered/coast cases. Velocity is expected to agree to roundoff during constant-acceleration intervals. Position expectations include the known semi-implicit Euler error:
+That test then independently recalculates drag, net force, and acceleration from the resulting velocity, proving ordinary recorded-state telemetry is not stale from the segment start.
@@ -53,3 +48,3 @@ They are applied independently to gravity-only, powered constant-acceleration, a
-```text
-p_numerical - p_analytical = 0.5 a t dt
-```
+A deliberately non-aligned active-drag step crosses burnout at `0.5 s` within `dt=1.0 s`. Its powered substep reaches `vx=2.75 m/s`; the coast substep recomputes drag as `-3.78125 N` from that burnout velocity and ends at `vx=0.859375 m/s`, `x=1.8046875 m`. The test also requires exactly one burnout sample.
+
+Impact telemetry is independently checked to ensure drag and acceleration are recalculated from the interpolated impact velocity. Ground handling remains interpolation of the discrete numerical segment and is not presented as an exact root solve.
@@ -57 +52 @@ p_numerical - p_analytical = 0.5 a t dt
-The suite also checks vertical horizontal displacement, zero thrust, zero gravity, and uniform zero-force motion.
+## Analytical vertical quadratic-drag fall
@@ -59 +54,13 @@ The suite also checks vertical horizontal displacement, zero thrust, zero gravit
-### Convergence
+The nonlinear reference uses:
+
+```text
+m = 2 kg
+g = 8 m/s^2
+rho = 2 kg/m^3
+Cd = 1
+A = 1 m^2
+k = 1 kg/m
+v_terminal = 4 m/s
+y0 = 100 m
+vy0 = 0
+```
@@ -61 +68 @@ The suite also checks vertical horizontal displacement, zero thrust, zero gravit
-An analytically referenced powered case runs with:
+At `t=1 s`, the independent continuous solution is:
@@ -64,3 +71,2 @@ An analytically referenced powered case runs with:
-dt = 0.02 s
-dt = 0.01 s
-dt = 0.005 s
+vy = -4 tanh(2)
+y = 100 - 2 ln(cosh(2))
@@ -69 +75,17 @@ dt = 0.005 s
-Position error must decrease monotonically and the error ratio must remain close to two, which is evidence of first-order convergence. A finer run from the same production integrator is not used as the sole correctness oracle.
+The high starting altitude prevents ground contact. At `dt=0.005 s`, the numerical state is `vy=-3.8598482081 m/s`, `y=97.3355269070 m`; the analytical state is `vy=-3.8561103203 m/s`, `y=97.3499945053 m`.
+
+## Measured timestep convergence
+
+The analytical fall produced these absolute errors:
+
+| `dt` (s) | `|velocity error|` (m/s) | `|altitude error|` (m) |
+| ---: | ---: | ---: |
+| 0.020 | 0.0148671763 | 0.0578690164 |
+| 0.010 | 0.0074621397 | 0.0289350701 |
+| 0.005 | 0.0037378878 | 0.0144675983 |
+
+Velocity error ratios as timestep halves are approximately `1.992` and `1.996`; altitude ratios are approximately `2.000` and `2.000`. This measured evidence is consistent with the expected first-order global behavior. It is not a claim of exact constant-acceleration error under active drag.
+
+## Terminal velocity
+
+With the same analytical parameters, tests calculate the expected forces independently:
@@ -71 +93,3 @@ Position error must decrease monotonically and the error ratio must remain close
-The default vertical flight also compares interpolated landing time at those three timesteps with the independently solved positive root of the piecewise powered/coast trajectory. Landing-time error must decrease and approximately halve with timestep.
+- at `vy=-4 m/s`, drag is `+16 N`, weight is `-16 N`, and acceleration is zero;
+- at `vy=-3 m/s`, net vertical force is `-7 N` and acceleration is downward; and
+- at `vy=-5 m/s`, net vertical force is `+9 N` and acceleration is upward.
@@ -73 +97 @@ The default vertical flight also compares interpolated landing time at those thr
-### Lifecycle and time separation
+No terminal-speed clamp exists.
@@ -75,8 +99 @@ The default vertical flight also compares interpolated landing time at those thr
-- full flight leaves the ground and later terminates while descending
-- reset restores state, history, flags, counter, and fractional accumulator
-- replaying the same elapsed-time sequence after reset gives exactly the same history
-- paused wall time does not accumulate
-- pre-launch wall time does not accumulate and pause can resume with retained fractional time
-- zero elapsed time at a very small valid timestep cannot fabricate a physics step
-- a representably subthreshold elapsed interval cannot fabricate a physics step
-- equal `0.5 s` elapsed durations partitioned at 30, 60, and 144 FPS produce the same 50 fixed physics steps and identical trajectory
+## Integrated lifecycle and time separation
@@ -84 +101 @@ The default vertical flight also compares interpolated landing time at those thr
-FPS validation feeds frame durations through the public accumulator rather than bypassing it with direct physics calls.
+The suite verifies:
@@ -86 +103,7 @@ FPS validation feeds frame durations through the public accumulator rather than
-### Rendering and application
+- physically coherent drag signs during powered ascent, coast ascent, and descent;
+- lower default-flight apogee with drag than in the zero-drag limit;
+- constant mass throughout active-drag flight;
+- deterministic reset/rerun with velocity-dependent feedback;
+- equal state and trajectory for active-drag elapsed time partitioned at 30, 60, and 144 FPS, including an exact burnout boundary;
+- paused RIGHT-arrow stepping advances one configured outer step, preserves fractional accumulator residue, remains paused, and retains burnout splitting; and
+- RIGHT is inactive before launch, while running, and after landing.
@@ -88,5 +111,31 @@ FPS validation feeds frame durations through the public accumulator rather than
-- physics modules have no Pygame import
-- world-to-screen conversion reverses only the vertical axis
-- drawing does not mutate physics state or trajectory
-- keyboard controls exercise launch/pause, reset, and exit
-- a dummy SDL display runs the application for a bounded number of frames and exits normally
+The default `dt=0.01 s` flight is numerically stable for the documented educational constants. The integrator remains explicit with respect to drag and is not claimed stable for arbitrary finite parameters or timesteps.
+
+## Rendering and application
+
+Automated evidence covers:
+
+- no Pygame dependency in configuration, physics, or simulation modules;
+- world and force-vector y-axis inversion only at rendering;
+- one shared display scale for thrust, gravity, drag, and net force;
+- four sentinel production force vectors reaching all four arrow endpoint calculations at that same scale;
+- Inspector presence of state, all force values, aerodynamic parameters, and implemented equations;
+- distinct Inspector labels for post-liftoff impact and terminal no-liftoff initial states;
+- the renderer reading `Simulation.current_forces` while containing no drag helper or drag equation implementation;
+- rendering with overlays enabled and disabled without mutating state, history, accumulator, or configuration;
+- F and I toggles changing presentation only;
+- SPACE, RIGHT, R, and ESC behavior; and
+- a bounded SDL dummy-display application run.
+
+The real SDL application launched successfully and remained live until intentionally interrupted. The available desktop-control layer could not attach to the unbundled Python window, so physical keyboard manipulation is not claimed. Separately rendered production frames were visually inspected at powered ascent, coast ascent, descent, and paused-after-single-step states. Arrow directions and numerical labels agreed with the force breakdowns; an initial label-overlap defect was corrected with small rendering-only lateral arrow origins while preserving direction and the common scale. Automated key-event tests cover SPACE, RIGHT, R, F, I, and ESC, and a scripted production-path paused step confirmed one `0.01 s` advance while remaining paused.
+
+Visual inspection supplements these automated checks but is not the scientific oracle.
+
+## Current Prompt 03 suite result
+
+After specialist review corrections, the complete suite reports:
+
+```text
+119 passed
+```
+
+Focused aerodynamic, analytical, convergence, integration, lifecycle, timing, and rendering groups also pass independently, as does the bounded SDL dummy application smoke test.
@@ -108,0 +158,2 @@ git diff --check
+Focused aerodynamic, analytical, convergence, integration, lifecycle, accumulator, and rendering tests are also run separately.
+
@@ -111 +162 @@ git diff --check
-Landing interpolation follows the discrete numerical segment; it is not an exact impact root. Event time, apogee, and landing metrics remain timestep-sensitive. The suite establishes correctness for the documented simplified equations and numerical contract, not agreement with real rockets. Real-flight comparison requires later calibration, uncertainty analysis, and measured data kept separate from evaluation data.
+The evidence establishes correctness for the documented still-air, constant-property, isotropic point-mass drag approximation and its numerical contract. It does not establish real-world aerodynamic accuracy. Landing values remain timestep-sensitive. Real-flight comparison requires measured vehicle data, calibration kept separate from evaluation, and explicit uncertainty analysis.
diff --git a/docs/decisions/decision_05_quadratic_drag_model.md b/docs/decisions/decision_05_quadratic_drag_model.md
new file mode 100644
index 0000000..664d26b
--- /dev/null
+++ b/docs/decisions/decision_05_quadratic_drag_model.md
@@ -0,0 +1,68 @@
+# Decision 05: Constant-property quadratic drag model
+
+- Date: 2026-08-28
+- Status: accepted
+- Related prompt: `docs/prompts/prompt_03_drag.md`
+- Supersedes: none
+
+## Decision
+
+Prompt 03 adds one aerodynamic effect: constant-property quadratic drag on the existing constant-mass 2D point rocket. The surrounding air is stationary, so rocket velocity relative to air is numerically equal to ground-frame rocket velocity. Air density, dimensionless drag coefficient, and one direction-independent effective reference area remain constant for the whole run.
+
+For air-relative velocity `v_air`:
+
+```text
+k = 0.5 rho Cd A
+F_drag = -k |v_air| v_air
+F_net = F_thrust + F_gravity + F_drag
+a = F_net / m
+```
+
+At zero speed, density, `Cd`, or area, drag is exactly zero. Integration retains fixed-step semi-implicit Euler: evaluate forces from segment-start time and velocity, update velocity, then update position from the new velocity. A step crossing burnout remains split exactly, and drag is recomputed from the burnout velocity for the coast substep. Recorded forces and acceleration are recalculated from each resulting state's time and velocity.
+
+The principal nonlinear reference is vertical fall from rest:
+
+```text
+v_terminal = sqrt(2 m g / (rho Cd A))
+vy(t) = -v_terminal tanh(g t / v_terminal)
+y(t) = y0 - (v_terminal^2 / g) ln(cosh(g t / v_terminal))
+```
+
+## Context and problem
+
+Prompt 02 deliberately excluded drag so gravity and thrust could be validated under constant acceleration. The next educational step needs an energy-removing velocity-dependent force that is vector-correct, inspectable, and independently testable without introducing atmosphere variation, wind, orientation, or real-vehicle calibration.
+
+The Physics Inspector also needs the exact component forces. One immutable `ForceBreakdown` therefore exposes thrust, gravity, drag, and net force to integration and presentation without introducing a general force-plugin framework.
+
+## Options considered
+
+- Constant-property quadratic drag in still air, the approved single-effect milestone.
+- Linear drag, which is analytically convenient but does not match Prompt 03's required `v^2` law.
+- Altitude-varying atmosphere or constant wind, both explicitly deferred because either would add another physical effect.
+- A drag-enable boolean, rejected because any zero aerodynamic scalar already supplies the exact Prompt 02 limiting case.
+- A higher-order or implicit integrator, rejected because the established semi-implicit Euler method remains understandable and demonstrates measured first-order convergence for the selected stable case.
+- Phase-specific ascent/descent drag signs, rejected in favor of one vector equation that works in every quadrant.
+
+## Rationale
+
+The selected model is the smallest scientifically coherent aerodynamic extension. It preserves SI units, constant mass, the half-open thrust interval, exact burnout segmentation, deterministic event handling, and rendering independence. The dot-product identity `F_drag dot v_air = -k |v_air|^3` establishes that drag removes energy for positive parameters. The analytical fall and terminal-speed equilibrium provide independent nonlinear checks.
+
+Defaults `rho=1.225 kg/m^3`, `Cd=0.75`, and `A=0.01 m^2` give the default 1 kg rocket a vertical gravity-only terminal speed of approximately `46.21 m/s`, producing visible but modest drag at `dt=0.01 s`. These are educational constants, not measured vehicle data.
+
+## Consequences and tradeoffs
+
+- Drag acts during powered flight, coast ascent, and descent and naturally reverses with velocity.
+- Setting density, `Cd`, or area to zero exactly recovers the Prompt 02 force path.
+- Acceleration is no longer constant with active drag, so Prompt 02's closed-form Euler position-error identity is limited to the zero-drag constant-acceleration case.
+- Semi-implicit Euler is explicit with respect to drag. Large `k |v| dt / m` can cause unphysical reversal or instability; no artificial clamp masks this limitation.
+- Constant density at all altitudes, constant `Cd`, and direction-independent area are simplified assumptions. The model omits wind, lift, compressibility, Mach/Reynolds effects, attitude, and aerodynamic stability.
+- READY exposes inactive zero forces to presentation rather than claiming an unmodeled pad-support equilibrium. A post-liftoff landed state exposes forces at the instant of interpolated impact, but no further motion is integrated. An unsupported ground start is labeled as a terminal no-liftoff initial state rather than impact.
+- The result is an educational point-mass approximation, not a calibrated real-flight or safety predictor.
+
+## Related prompt records
+
+- `docs/prompts/prompt_03_drag.md`
+
+## Superseding decision
+
+None.
diff --git a/docs/product/PROJECT_UNDERSTANDING.md b/docs/product/PROJECT_UNDERSTANDING.md
index 40eb697..929b2a1 100644
--- a/docs/product/PROJECT_UNDERSTANDING.md
+++ b/docs/product/PROJECT_UNDERSTANDING.md
@@ -5,3 +5 @@
-RocketSim is a trustworthy, understandable 2D model-rocket simulator rather than an engineering-grade launch predictor. Prompt 02 completes the first powered point-mass flight milestone: a visible Pygame application backed by a headless, deterministic physics core and independent numerical evidence.
-
-Prompt 03 has not begun.
+RocketSim is a trustworthy, understandable 2D model-rocket learning simulator rather than an engineering-grade launch predictor. Prompt 03 completes the constant-property quadratic-drag milestone and adds an educational Physics Inspector without adding another physical model.
@@ -13 +11 @@ The rocket is a constant-mass point in a 2D flat world. Internally, all quantiti
-The only forces are:
+The forces are:
@@ -15,2 +13,3 @@ The only forces are:
-- constant gravity `(0, -m g)`; and
-- constant thrust `T(cos(theta), sin(theta))` during `0 <= t < burn_time`.
+- constant gravity `(0, -m g)`;
+- constant thrust `T(cos(theta), sin(theta))` during `0 <= t < burn_time`; and
+- quadratic drag `-0.5 rho Cd A |v_air| v_air`.
@@ -18 +17 @@ The only forces are:
-The default configuration is `m = 1 kg`, `T = 20 N`, `burn_time = 1 s`, `theta = 90 degrees`, `g = 9.81 m/s²`, and `dt = 0.01 s`. It is intentionally capable of liftoff. A ground start is accepted only when its initial vertical velocity is non-negative and its first constant-force numerical segment ends above ground. Otherwise it terminates at the initial ground state without recording negative altitude; no pad normal-force model is claimed.
+Air is stationary, so rocket velocity relative to air is numerically equal to ground-frame rocket velocity. Density, drag coefficient, and reference area are fixed for a complete run. The default educational constants are `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`; they are not calibration of a particular rocket. Setting any one of these scalars to zero recovers the validated Prompt 02 no-drag model through the same force path.
@@ -23,2 +22,2 @@ The default configuration is `m = 1 kg`, `T = 20 N`, `burn_time = 1 s`, `theta =
-src/rocket_sim/config.py       validated immutable configuration and neutral Vector2
-src/rocket_sim/physics.py      force equations and semi-implicit Euler segment update
+src/rocket_sim/config.py       immutable Vector2 and validated run constants
+src/rocket_sim/physics.py      thrust, gravity, drag, force breakdown, and Euler segment
@@ -26,2 +25,2 @@ src/rocket_sim/simulation.py   state, lifecycle, fixed-step clock, events, and h
-src/rocket_sim/rendering.py    world-to-screen transform, drawing, and telemetry
-src/rocket_sim/app.py          Pygame loop and controls
+src/rocket_sim/rendering.py    world transform, force arrows, and Physics Inspector
+src/rocket_sim/app.py          Pygame loop and educational controls
@@ -31 +30 @@ src/rocket_sim/__main__.py     python -m rocket_sim entry point
-The physics modules do not import Pygame. Rendering reads immutable state samples and cannot change simulation results.
+The physics modules do not import Pygame. Rendering consumes `Simulation.current_forces`, the same immutable `ForceBreakdown` calculated by the production physics layer. Display scaling and visibility toggles cannot alter physical values or state.
@@ -35,6 +34,8 @@ The physics modules do not import Pygame. Rendering reads immutable state sample
-- Each constant-force segment uses semi-implicit Euler: velocity is updated before position.
-- The display loop supplies elapsed wall time to a compensated accumulator; only complete fixed `physics_dt_s` steps advance the model, with no epsilon-created time.
-- Paused or pre-launch wall time is not accumulated, and reset clears accumulator residue.
-- A step spanning burnout is divided at the exact half-open burn boundary, preventing excess or missing thrust impulse.
-- Acceleration telemetry is the instantaneous acceleration at the resulting state time; at exact burnout it therefore shows coast acceleration.
-- Ground return is detected only after liftoff. The first descending discrete segment that crosses `y = 0` is linearly interpolated to the ground, then the flight becomes terminal. This is deterministic interpolation of the discrete numerical path, not an exact impact solve. A terminal sample represents the instant of impact, so thrust and instantaneous acceleration still reflect that time even when impact precedes burnout.
+- Every numerical segment evaluates thrust, gravity, and drag from its starting time and velocity.
+- Semi-implicit Euler then updates velocity before position.
+- Drag makes true continuous acceleration velocity-dependent, so Prompt 02's constant-acceleration position-error identity applies only when drag is disabled.
+- The display loop supplies elapsed wall time to a compensated accumulator; only complete fixed timesteps advance the model.
+- A step spanning burnout is divided at the exact half-open burn boundary. The coast substep recomputes drag from the burnout velocity.
+- Recorded acceleration and displayed forces are instantaneous values recalculated from the resulting state's time and velocity, including exact burnout and interpolated impact states.
+- Ground return remains deterministic interpolation of the first descending discrete crossing after liftoff, not an exact collision solve.
+- A paused RIGHT-arrow command advances exactly one normal configured fixed step, keeps the simulation paused, and preserves fractional accumulator time unless the step lands.
@@ -42 +43,3 @@ The physics modules do not import Pygame. Rendering reads immutable state sample
-## Validation status
+## Educational presentation
+
+The Pygame application shows powered and coast trajectory segments, current phase and burnout status, thrust/gravity/drag/net-force arrows, numerical force components and magnitudes, aerodynamic parameters, and the implemented equations. READY explicitly reports forces as inactive alongside zero stored acceleration; it does not invent a pad normal force.
@@ -44 +47,3 @@ The physics modules do not import Pygame. Rendering reads immutable state sample
-The headless test suite covers configuration validation, force signs and components, burn-boundary predicates, constant mass, Euler ordering, analytical gravity/powered/piecewise motion, non-aligned burnout splitting, limiting cases, first-order timestep convergence, reset determinism, interpolated ground return, 30/60/144 FPS partition independence, coordinate conversion, rendering non-mutation, controls, package import, and a bounded dummy-display application smoke test.
+Controls are SPACE launch/pause/resume, RIGHT single-step while paused, R reset, F force overlay, I Physics Inspector, and ESC exit.
+
+## Validation status
@@ -46 +51 @@ The headless test suite covers configuration validation, force signs and compone
-Analytical expected values are calculated independently in tests rather than through production force or integration helpers.
+The suite preserves Prompt 02 with explicitly disabled drag and adds independent vector-force oracles, all quadrants, exact zero cases, `v^2` scaling, terminal velocity, a closed-form vertical quadratic-drag fall, measured first-order timestep convergence, active-drag burnout, active-drag reset and FPS independence, paused stepping, rendering isolation, Inspector sourcing, and a bounded SDL dummy application smoke test.
@@ -50 +55 @@ Analytical expected values are calculated independently in tests rather than thr
-There is no drag, variable mass, real motor curve, atmosphere, wind, recovery, collision dynamics, rotation, stability, guidance, control, experiment export, calibration, or uncertainty model. The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction.
+Density, `Cd`, and effective reference area are constant and direction-independent. There is no wind, altitude-varying atmosphere, lift, compressibility, Mach/Reynolds dependence, variable mass, real motor curve, recovery, collision dynamics, rotation, stability, guidance, control, plotting, experiment export, calibration, or uncertainty model. Semi-implicit Euler is explicit with respect to drag and can become unstable for sufficiently large timestep or speed; no artificial clamp conceals that limitation.
@@ -52 +57 @@ There is no drag, variable mass, real motor curve, atmosphere, wind, recovery, c
-The next milestone remains out of scope for Prompt 02.
+The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction. Prompt 04 has not begun.
diff --git a/src/rocket_sim/__init__.py b/src/rocket_sim/__init__.py
index 1dbf6ce..c9f1d0f 100644
--- a/src/rocket_sim/__init__.py
+++ b/src/rocket_sim/__init__.py
@@ -3,0 +4 @@ from .config import SimulationConfig, Vector2
+from .physics import ForceBreakdown
@@ -9,0 +11 @@ __all__ = [
+    "ForceBreakdown",
diff --git a/src/rocket_sim/app.py b/src/rocket_sim/app.py
index dac8f3b..7ab9b54 100644
--- a/src/rocket_sim/app.py
+++ b/src/rocket_sim/app.py
@@ -11 +11 @@ from .simulation import Simulation
-WINDOW_SIZE = (900, 700)
+WINDOW_SIZE = (1200, 720)
@@ -15 +15,3 @@ DISPLAY_FPS = 60
-def handle_keydown(key: int, simulation: Simulation) -> bool:
+def handle_keydown(
+    key: int, simulation: Simulation, renderer: Renderer | None = None
+) -> bool:
@@ -23,0 +26,6 @@ def handle_keydown(key: int, simulation: Simulation) -> bool:
+    elif key == pygame.K_RIGHT:
+        simulation.single_step_paused()
+    elif key == pygame.K_f and renderer is not None:
+        renderer.toggle_force_vectors()
+    elif key == pygame.K_i and renderer is not None:
+        renderer.toggle_inspector()
@@ -36 +44 @@ def run(max_frames: int | None = None) -> int:
-        pygame.display.set_caption("RocketSim — constant-thrust Milestone 1")
+        pygame.display.set_caption("RocketSim - quadratic-drag Physics Inspector")
@@ -49 +57 @@ def run(max_frames: int | None = None) -> int:
-                    running = handle_keydown(event.key, simulation)
+                    running = handle_keydown(event.key, simulation, renderer)
diff --git a/src/rocket_sim/config.py b/src/rocket_sim/config.py
index 8992897..e8e38fa 100644
--- a/src/rocket_sim/config.py
+++ b/src/rocket_sim/config.py
@@ -44 +44 @@ class SimulationConfig:
-    """Physical parameters for one deterministic Milestone 1 run."""
+    """Physical parameters for one deterministic Milestone 2 run."""
@@ -50,0 +51,3 @@ class SimulationConfig:
+    air_density_kg_m3: float = 1.225
+    drag_coefficient: float = 0.75
+    reference_area_m2: float = 0.01
@@ -61,0 +65,3 @@ class SimulationConfig:
+            "air_density_kg_m3": self.air_density_kg_m3,
+            "drag_coefficient": self.drag_coefficient,
+            "reference_area_m2": self.reference_area_m2,
@@ -76,0 +83,6 @@ class SimulationConfig:
+        if self.air_density_kg_m3 < 0.0:
+            raise ValueError("air_density_kg_m3 must be non-negative")
+        if self.drag_coefficient < 0.0:
+            raise ValueError("drag_coefficient must be non-negative")
+        if self.reference_area_m2 < 0.0:
+            raise ValueError("reference_area_m2 must be non-negative")
diff --git a/src/rocket_sim/physics.py b/src/rocket_sim/physics.py
index e675243..6dbd35e 100644
--- a/src/rocket_sim/physics.py
+++ b/src/rocket_sim/physics.py
@@ -4,0 +5 @@ from __future__ import annotations
+from dataclasses import dataclass
@@ -9,0 +11,15 @@ from .config import SimulationConfig, Vector2
+@dataclass(frozen=True, slots=True)
+class ForceBreakdown:
+    """Named physical forces evaluated for one instantaneous state."""
+
+    thrust_n: Vector2
+    gravity_n: Vector2
+    drag_n: Vector2
+    net_n: Vector2
+
+    @classmethod
+    def zero(cls) -> ForceBreakdown:
+        zero = Vector2(0.0, 0.0)
+        return cls(thrust_n=zero, gravity_n=zero, drag_n=zero, net_n=zero)
+
+
@@ -29,2 +45,30 @@ def thrust_force_n(config: SimulationConfig, time_s: float) -> Vector2:
-def acceleration_m_s2(config: SimulationConfig, time_s: float) -> Vector2:
-    """Return net acceleration from thrust and gravity at ``time_s``."""
+def drag_force_n(
+    config: SimulationConfig, air_relative_velocity_m_s: Vector2
+) -> Vector2:
+    """Return constant-property quadratic drag in still air."""
+
+    speed_m_s = air_relative_velocity_m_s.magnitude
+    if (
+        speed_m_s == 0.0
+        or config.air_density_kg_m3 == 0.0
+        or config.drag_coefficient == 0.0
+        or config.reference_area_m2 == 0.0
+    ):
+        return Vector2(0.0, 0.0)
+
+    scale = (
+        -0.5
+        * config.air_density_kg_m3
+        * config.drag_coefficient
+        * config.reference_area_m2
+        * speed_m_s
+    )
+    return air_relative_velocity_m_s * scale
+
+
+def force_breakdown_n(
+    config: SimulationConfig,
+    time_s: float,
+    air_relative_velocity_m_s: Vector2,
+) -> ForceBreakdown:
+    """Return thrust, gravity, drag, and their exact vector sum."""
@@ -34 +78,18 @@ def acceleration_m_s2(config: SimulationConfig, time_s: float) -> Vector2:
-    return (thrust + gravity) * (1.0 / config.mass_kg)
+    drag = drag_force_n(config, air_relative_velocity_m_s)
+    return ForceBreakdown(
+        thrust_n=thrust,
+        gravity_n=gravity,
+        drag_n=drag,
+        net_n=thrust + gravity + drag,
+    )
+
+
+def acceleration_m_s2(
+    config: SimulationConfig,
+    time_s: float,
+    air_relative_velocity_m_s: Vector2,
+) -> Vector2:
+    """Return acceleration from the instantaneous force breakdown."""
+
+    forces = force_breakdown_n(config, time_s, air_relative_velocity_m_s)
+    return forces.net_n * (1.0 / config.mass_kg)
@@ -43 +104 @@ def semi_implicit_euler(
-    """Advance one constant-acceleration segment using updated velocity."""
+    """Advance one force-frozen segment using updated velocity."""
diff --git a/src/rocket_sim/rendering.py b/src/rocket_sim/rendering.py
index ae953bb..ec4f67e 100644
--- a/src/rocket_sim/rendering.py
+++ b/src/rocket_sim/rendering.py
@@ -1 +1 @@
-"""Pygame presentation for RocketSim world state."""
+"""Pygame presentation for RocketSim world state and physical forces."""
@@ -5,0 +6 @@ from dataclasses import dataclass, field
+import math
@@ -9,0 +11 @@ from .config import Vector2
+from .physics import ForceBreakdown
@@ -12,0 +15,13 @@ from .simulation import FlightPhase, Simulation
+FORCE_COLORS: dict[str, tuple[int, int, int]] = {
+    "Thrust": (255, 174, 66),
+    "Gravity": (106, 168, 255),
+    "Drag": (238, 112, 214),
+    "Net": (102, 221, 154),
+}
+
+CONTROL_ROWS = (
+    "SPACE launch/pause  RIGHT single-step  R reset  ESC exit",
+    "F force vectors  I Physics Inspector",
+)
+
+
@@ -25,0 +41,82 @@ def world_to_screen(
+def force_vector_endpoint(
+    origin_px: tuple[int, int],
+    force_n: Vector2,
+    pixels_per_newton: float,
+) -> tuple[int, int]:
+    """Map one world-frame force to a screen endpoint for drawing only."""
+
+    return (
+        round(origin_px[0] + force_n.x * pixels_per_newton),
+        round(origin_px[1] - force_n.y * pixels_per_newton),
+    )
+
+
+def physics_inspector_rows(
+    simulation: Simulation, forces: ForceBreakdown
+) -> tuple[str, ...]:
+    """Format inspector values from the production force breakdown."""
+
+    state = simulation.state
+    if state.phase is FlightPhase.READY:
+        phase = "READY (forces inactive)"
+    elif state.phase is FlightPhase.LANDED:
+        phase = (
+            "LANDED / impact state"
+            if state.has_lifted_off
+            else "NO LIFTOFF / terminal initial state"
+        )
+    elif simulation.is_paused:
+        phase = f"PAUSED / {state.phase.value.upper()}"
+    else:
+        phase = state.phase.value.upper()
+
+    if state.phase is FlightPhase.READY:
+        burnout = f"pending at {simulation.config.burn_time_s:.3f} s"
+    elif state.time_s >= simulation.config.burn_time_s:
+        burnout = f"complete at {simulation.config.burn_time_s:.3f} s"
+    else:
+        burnout = f"pending at {simulation.config.burn_time_s:.3f} s"
+
+    def force_row(name: str, force: Vector2) -> str:
+        return (
+            f"{name:<7} ({force.x:7.3f}, {force.y:7.3f}) N"
+            f"  |F|={force.magnitude:7.3f}"
+        )
+
+    return (
+        "PHYSICS INSPECTOR",
+        "",
+        f"Phase: {phase}",
+        f"Burnout: {burnout}",
+        f"Time: {state.time_s:7.3f} s",
+        f"Position: ({state.position_m.x:7.3f}, {state.position_m.y:7.3f}) m",
+        f"Velocity: ({state.velocity_m_s.x:7.3f}, {state.velocity_m_s.y:7.3f}) m/s",
+        f"Speed: {state.velocity_m_s.magnitude:7.3f} m/s",
+        (
+            "Acceleration: "
+            f"({state.acceleration_m_s2.x:7.3f}, "
+            f"{state.acceleration_m_s2.y:7.3f}) m/s^2"
+        ),
+        f"Mass: {state.mass_kg:7.3f} kg",
+        "",
+        "FORCES",
+        force_row("Thrust", forces.thrust_n),
+        force_row("Gravity", forces.gravity_n),
+        force_row("Drag", forces.drag_n),
+        force_row("Net", forces.net_n),
+        "",
+        "PARAMETERS (constant)",
+        f"rho: {simulation.config.air_density_kg_m3:.4f} kg/m^3",
+        f"Cd: {simulation.config.drag_coefficient:.4f}",
+        f"Area: {simulation.config.reference_area_m2:.4f} m^2",
+        "",
+        "EQUATIONS",
+        "Fg = (0, -m g)",
+        "Ft = T(cos(theta), sin(theta))",
+        "Fd = -0.5 rho Cd A |v_air| v_air",
+        "Fnet = Ft + Fg + Fd",
+        "a = Fnet / m",
+        "Still air: v_air = v_rocket",
+    )
+
+
@@ -28,2 +125,2 @@ class Renderer:
-    width_px: int = 900
-    height_px: int = 700
+    width_px: int = 1200
+    height_px: int = 720
@@ -31 +128,5 @@ class Renderer:
-    ground_y_px: int = 620
+    ground_y_px: int = 650
+    world_width_px: int = 800
+    force_pixels_per_newton: float = 5.0
+    show_force_vectors: bool = True
+    show_inspector: bool = True
@@ -32,0 +134,2 @@ class Renderer:
+    _small_font: pygame.font.Font = field(init=False, repr=False)
+    _heading_font: pygame.font.Font = field(init=False, repr=False)
@@ -35 +138,3 @@ class Renderer:
-        self._font = pygame.font.Font(None, 25)
+        self._font = pygame.font.Font(None, 24)
+        self._small_font = pygame.font.Font(None, 18)
+        self._heading_font = pygame.font.Font(None, 28)
@@ -39 +144,7 @@ class Renderer:
-        return (self.width_px / 2.0, float(self.ground_y_px))
+        return (self.world_width_px / 2.0, float(self.ground_y_px))
+
+    def toggle_force_vectors(self) -> None:
+        self.show_force_vectors = not self.show_force_vectors
+
+    def toggle_inspector(self) -> None:
+        self.show_inspector = not self.show_inspector
@@ -46 +157,6 @@ class Renderer:
-            pygame.Rect(0, self.ground_y_px, self.width_px, self.height_px),
+            pygame.Rect(
+                0,
+                self.ground_y_px,
+                self.world_width_px,
+                self.height_px - self.ground_y_px,
+            ),
@@ -52 +168,8 @@ class Renderer:
-            (self.width_px, self.ground_y_px),
+            (self.world_width_px, self.ground_y_px),
+            2,
+        )
+        pygame.draw.line(
+            surface,
+            (86, 102, 126),
+            (self.world_width_px, 0),
+            (self.world_width_px, self.height_px),
@@ -56,8 +179,2 @@ class Renderer:
-        points = [
-            world_to_screen(sample.position_m, self.origin_px, self.pixels_per_metre)
-            for sample in simulation.trajectory
-        ]
-        if len(points) >= 2:
-            pygame.draw.lines(surface, (96, 184, 255), False, points, 2)
-
-        rocket_x, rocket_y = world_to_screen(
+        self._draw_trajectory(surface, simulation)
+        rocket_position = world_to_screen(
@@ -67,0 +185,41 @@ class Renderer:
+        self._draw_rocket(surface, rocket_position)
+
+        forces = simulation.current_forces
+        if self.show_force_vectors:
+            self._draw_force_vectors(surface, rocket_position, forces)
+
+        self._draw_world_status(surface, simulation)
+        if self.show_inspector:
+            self._draw_inspector(surface, simulation, forces)
+        else:
+            rendered = self._font.render(
+                "Physics Inspector hidden - press I", True, (182, 194, 211)
+            )
+            surface.blit(rendered, (self.world_width_px + 20, 22))
+
+    def _draw_trajectory(
+        self, surface: pygame.Surface, simulation: Simulation
+    ) -> None:
+        samples = simulation.trajectory
+        for before, after in zip(samples, samples[1:], strict=False):
+            color = (
+                (255, 174, 66)
+                if before.phase is FlightPhase.POWERED
+                else (96, 184, 255)
+            )
+            pygame.draw.line(
+                surface,
+                color,
+                world_to_screen(
+                    before.position_m, self.origin_px, self.pixels_per_metre
+                ),
+                world_to_screen(
+                    after.position_m, self.origin_px, self.pixels_per_metre
+                ),
+                2,
+            )
+
+    def _draw_rocket(
+        self, surface: pygame.Surface, position_px: tuple[int, int]
+    ) -> None:
+        rocket_x, rocket_y = position_px
@@ -71 +229,5 @@ class Renderer:
-            [(rocket_x, rocket_y - 12), (rocket_x - 6, rocket_y + 8), (rocket_x + 6, rocket_y + 8)],
+            [
+                (rocket_x, rocket_y - 12),
+                (rocket_x - 6, rocket_y + 8),
+                (rocket_x + 6, rocket_y + 8),
+            ],
@@ -74 +236,60 @@ class Renderer:
-        self._draw_telemetry(surface, simulation)
+    def _draw_force_vectors(
+        self,
+        surface: pygame.Surface,
+        origin_px: tuple[int, int],
+        forces: ForceBreakdown,
+    ) -> None:
+        entries = (
+            ("Thrust", forces.thrust_n, -36, (-82, -8)),
+            ("Gravity", forces.gravity_n, -12, (-92, -8)),
+            ("Drag", forces.drag_n, 12, (5, -8)),
+            ("Net", forces.net_n, 36, (5, -8)),
+        )
+        for name, force, origin_offset_x, label_offset in entries:
+            arrow_origin = (origin_px[0] + origin_offset_x, origin_px[1])
+            self._draw_force_arrow(
+                surface,
+                arrow_origin,
+                force,
+                name,
+                FORCE_COLORS[name],
+                label_offset,
+            )
+
+    def _draw_force_arrow(
+        self,
+        surface: pygame.Surface,
+        origin_px: tuple[int, int],
+        force_n: Vector2,
+        label: str,
+        color: tuple[int, int, int],
+        label_offset_px: tuple[int, int],
+    ) -> None:
+        if force_n.magnitude == 0.0:
+            return
+        endpoint = force_vector_endpoint(
+            origin_px, force_n, self.force_pixels_per_newton
+        )
+        pygame.draw.line(surface, color, origin_px, endpoint, 3)
+
+        angle = math.atan2(endpoint[1] - origin_px[1], endpoint[0] - origin_px[0])
+        arrow_size = 8.0
+        left = (
+            endpoint[0] - arrow_size * math.cos(angle - math.pi / 6.0),
+            endpoint[1] - arrow_size * math.sin(angle - math.pi / 6.0),
+        )
+        right = (
+            endpoint[0] - arrow_size * math.cos(angle + math.pi / 6.0),
+            endpoint[1] - arrow_size * math.sin(angle + math.pi / 6.0),
+        )
+        pygame.draw.polygon(surface, color, [endpoint, left, right])
+        rendered = self._small_font.render(
+            f"{label} {force_n.magnitude:.2f} N", True, color
+        )
+        surface.blit(
+            rendered,
+            (
+                endpoint[0] + label_offset_px[0],
+                endpoint[1] + label_offset_px[1],
+            ),
+        )
@@ -76 +297,3 @@ class Renderer:
-    def _draw_telemetry(self, surface: pygame.Surface, simulation: Simulation) -> None:
+    def _draw_world_status(
+        self, surface: pygame.Surface, simulation: Simulation
+    ) -> None:
@@ -79 +302 @@ class Renderer:
-            status = "READY"
+            phase = "READY"
@@ -81 +304 @@ class Renderer:
-            status = "LANDED"
+            phase = "LANDED"
@@ -83 +306 @@ class Renderer:
-            status = f"PAUSED / {state.phase.value.upper()}"
+            phase = f"PAUSED / {state.phase.value.upper()}"
@@ -85 +308 @@ class Renderer:
-            status = state.phase.value.upper()
+            phase = state.phase.value.upper()
@@ -88,9 +311,2 @@ class Renderer:
-            "SPACE launch/pause  |  R reset  |  ESC exit",
-            f"Phase: {status}",
-            f"Time: {state.time_s:7.3f} s",
-            f"Position: ({state.position_m.x:7.3f}, {state.position_m.y:7.3f}) m",
-            f"Velocity: ({state.velocity_m_s.x:7.3f}, {state.velocity_m_s.y:7.3f}) m/s",
-            f"Speed: {state.velocity_m_s.magnitude:7.3f} m/s",
-            f"Acceleration: ({state.acceleration_m_s2.x:7.3f}, {state.acceleration_m_s2.y:7.3f}) m/s²",
-            f"Mass: {state.mass_kg:7.3f} kg",
-            f"Thrust: {simulation.current_thrust_n:7.3f} N",
+            *CONTROL_ROWS,
+            f"Phase: {phase}    t={state.time_s:.3f} s",
@@ -100,0 +317,17 @@ class Renderer:
+
+    def _draw_inspector(
+        self,
+        surface: pygame.Surface,
+        simulation: Simulation,
+        forces: ForceBreakdown,
+    ) -> None:
+        panel_x = self.world_width_px + 18
+        rows = physics_inspector_rows(simulation, forces)
+        for index, text in enumerate(rows):
+            if index == 0:
+                rendered = self._heading_font.render(text, True, (245, 214, 96))
+            elif text in {"FORCES", "PARAMETERS (constant)", "EQUATIONS"}:
+                rendered = self._font.render(text, True, (142, 203, 255))
+            else:
+                rendered = self._small_font.render(text, True, (232, 238, 247))
+            surface.blit(rendered, (panel_x, 16 + index * 23))
diff --git a/src/rocket_sim/simulation.py b/src/rocket_sim/simulation.py
index 2791a80..a156ef3 100644
--- a/src/rocket_sim/simulation.py
+++ b/src/rocket_sim/simulation.py
@@ -10 +10,6 @@ from .config import SimulationConfig, Vector2
-from .physics import acceleration_m_s2, semi_implicit_euler
+from .physics import (
+    ForceBreakdown,
+    acceleration_m_s2,
+    force_breakdown_n,
+    semi_implicit_euler,
+)
@@ -75,0 +81,6 @@ class Simulation:
+        return self.current_forces.thrust_n.magnitude
+
+    @property
+    def current_forces(self) -> ForceBreakdown:
+        """Return forces at the current state, inactive while still ready."""
+
@@ -77,4 +88,6 @@ class Simulation:
-            return 0.0
-        if 0.0 <= self._state.time_s < self.config.burn_time_s:
-            return self.config.thrust_n
-        return 0.0
+            return ForceBreakdown.zero()
+        return force_breakdown_n(
+            self.config,
+            self._state.time_s,
+            self._state.velocity_m_s,
+        )
@@ -99 +112,3 @@ class Simulation:
-        initial_acceleration = acceleration_m_s2(self.config, 0.0)
+        initial_acceleration = acceleration_m_s2(
+            self.config, 0.0, self._state.velocity_m_s
+        )
@@ -167,2 +182 @@ class Simulation:
-            self._advance_fixed_step(dt)
-            self._physics_step_count += 1
+            self._take_fixed_step()
@@ -192,0 +207,12 @@ class Simulation:
+        self._take_fixed_step()
+        return True
+
+    def single_step_paused(self) -> bool:
+        """Advance one production fixed step during a live paused flight."""
+
+        if not self.is_paused:
+            return False
+        self._take_fixed_step()
+        return True
+
+    def _take_fixed_step(self) -> None:
@@ -195 +220,0 @@ class Simulation:
-        return True
@@ -217 +242,3 @@ class Simulation:
-        acceleration = acceleration_m_s2(self.config, previous.time_s)
+        acceleration = acceleration_m_s2(
+            self.config, previous.time_s, previous.velocity_m_s
+        )
@@ -248 +275,3 @@ class Simulation:
-                acceleration_m_s2=acceleration_m_s2(self.config, impact_time_s),
+                acceleration_m_s2=acceleration_m_s2(
+                    self.config, impact_time_s, impact_velocity
+                ),
@@ -264 +293 @@ class Simulation:
-                    self.config, previous.time_s
+                    self.config, previous.time_s, previous.velocity_m_s
@@ -279 +308,3 @@ class Simulation:
-            acceleration_m_s2=acceleration_m_s2(self.config, target_time_s),
+            acceleration_m_s2=acceleration_m_s2(
+                self.config, target_time_s, trial_velocity
+            ),
diff --git a/tests/test_aerodynamics.py b/tests/test_aerodynamics.py
new file mode 100644
index 0000000..4e1ca64
--- /dev/null
+++ b/tests/test_aerodynamics.py
@@ -0,0 +1,140 @@
+import math
+
+import pytest
+
+from rocket_sim import SimulationConfig, Vector2
+from rocket_sim.physics import (
+    acceleration_m_s2,
+    drag_force_n,
+    force_breakdown_n,
+)
+
+
+def _aerodynamic_config(**overrides: float) -> SimulationConfig:
+    values = {
+        "mass_kg": 2.0,
+        "thrust_n": 10.0,
+        "burn_time_s": 2.0,
+        "launch_angle_rad": 0.0,
+        "gravity_m_s2": 3.0,
+        "air_density_kg_m3": 2.0,
+        "drag_coefficient": 0.5,
+        "reference_area_m2": 0.25,
+    }
+    values.update(overrides)
+    return SimulationConfig(**values)
+
+
+def test_drag_is_exactly_zero_at_zero_air_relative_speed() -> None:
+    assert drag_force_n(
+        _aerodynamic_config(), Vector2(0.0, 0.0)
+    ) == Vector2(0.0, 0.0)
+
+
+@pytest.mark.parametrize(
+    "disabled_parameter",
+    ("air_density_kg_m3", "drag_coefficient", "reference_area_m2"),
+)
+def test_zero_aerodynamic_parameter_disables_drag_exactly(
+    disabled_parameter: str,
+) -> None:
+    config = _aerodynamic_config(**{disabled_parameter: 0.0})
+
+    assert drag_force_n(config, Vector2(3.0, 4.0)) == Vector2(0.0, 0.0)
+
+
+@pytest.mark.parametrize(
+    ("velocity", "expected_force"),
+    [
+        (Vector2(4.0, 0.0), Vector2(-2.0, 0.0)),
+        (Vector2(-4.0, 0.0), Vector2(2.0, 0.0)),
+        (Vector2(0.0, 4.0), Vector2(0.0, -2.0)),
+        (Vector2(0.0, -4.0), Vector2(0.0, 2.0)),
+        (Vector2(3.0, 4.0), Vector2(-1.875, -2.5)),
+        (Vector2(-3.0, 4.0), Vector2(1.875, -2.5)),
+        (Vector2(3.0, -4.0), Vector2(-1.875, 2.5)),
+        (Vector2(-3.0, -4.0), Vector2(1.875, 2.5)),
+    ],
+)
+def test_drag_has_independent_expected_direction_and_components(
+    velocity: Vector2, expected_force: Vector2
+) -> None:
+    force = drag_force_n(_aerodynamic_config(), velocity)
+
+    assert force.x == pytest.approx(expected_force.x, abs=1e-12)
+    assert force.y == pytest.approx(expected_force.y, abs=1e-12)
+    assert force.x * velocity.x + force.y * velocity.y < 0.0
+
+
+def test_drag_magnitude_matches_scalar_quadratic_equation() -> None:
+    force = drag_force_n(_aerodynamic_config(), Vector2(3.0, 4.0))
+
+    assert force.magnitude == pytest.approx(3.125, abs=1e-12)
+
+
+def test_doubling_speed_multiplies_drag_magnitude_by_four() -> None:
+    config = _aerodynamic_config()
+    slower = drag_force_n(config, Vector2(3.0, 4.0))
+    faster = drag_force_n(config, Vector2(6.0, 8.0))
+
+    assert faster.magnitude == pytest.approx(4.0 * slower.magnitude, abs=1e-12)
+
+
+def test_reversing_velocity_reverses_drag_force() -> None:
+    config = _aerodynamic_config()
+    forward = drag_force_n(config, Vector2(3.0, -4.0))
+    reverse = drag_force_n(config, Vector2(-3.0, 4.0))
+
+    assert reverse == forward * -1.0
+
+
+def test_force_breakdown_and_acceleration_match_literal_oracle() -> None:
+    config = _aerodynamic_config()
+    velocity = Vector2(3.0, 4.0)
+
+    forces = force_breakdown_n(config, 0.25, velocity)
+    acceleration = acceleration_m_s2(config, 0.25, velocity)
+
+    assert forces.thrust_n.x == pytest.approx(10.0, abs=1e-12)
+    assert forces.thrust_n.y == pytest.approx(0.0, abs=1e-12)
+    assert forces.gravity_n == Vector2(0.0, -6.0)
+    assert forces.drag_n == Vector2(-1.875, -2.5)
+    assert forces.net_n == Vector2(8.125, -8.5)
+    assert acceleration == Vector2(4.0625, -4.25)
+
+
+def test_terminal_velocity_is_force_equilibrium_with_restoring_signs() -> None:
+    config = SimulationConfig(
+        mass_kg=2.0,
+        thrust_n=0.0,
+        burn_time_s=0.0,
+        gravity_m_s2=8.0,
+        air_density_kg_m3=2.0,
+        drag_coefficient=1.0,
+        reference_area_m2=1.0,
+        initial_position_m=Vector2(0.0, 100.0),
+    )
+
+    at_terminal = acceleration_m_s2(config, 1.0, Vector2(0.0, -4.0))
+    below_terminal = acceleration_m_s2(config, 1.0, Vector2(0.0, -3.0))
+    above_terminal = acceleration_m_s2(config, 1.0, Vector2(0.0, -5.0))
+
+    assert at_terminal == Vector2(0.0, 0.0)
+    assert below_terminal.y == pytest.approx(-3.5, abs=1e-12)
+    assert above_terminal.y == pytest.approx(4.5, abs=1e-12)
+
+
+def test_default_terminal_speed_is_moderate_for_educational_scenario() -> None:
+    config = SimulationConfig()
+    expected = math.sqrt(
+        2.0
+        * config.mass_kg
+        * config.gravity_m_s2
+        / (
+            config.air_density_kg_m3
+            * config.drag_coefficient
+            * config.reference_area_m2
+        )
+    )
+
+    assert expected == pytest.approx(46.2116, rel=1e-5)
diff --git a/tests/test_analytical_validation.py b/tests/test_analytical_validation.py
index 9e784c0..112ac7e 100644
--- a/tests/test_analytical_validation.py
+++ b/tests/test_analytical_validation.py
@@ -20,0 +21 @@ def test_gravity_only_matches_independent_projectile_reference() -> None:
+        air_density_kg_m3=0.0,
@@ -53,0 +55 @@ def test_powered_motion_matches_independent_constant_acceleration_reference() ->
+        air_density_kg_m3=0.0,
@@ -80 +82 @@ def test_piecewise_powered_and_coast_motion_matches_closed_form_error() -> None:
-    config = SimulationConfig(physics_dt_s=dt)
+    config = SimulationConfig(physics_dt_s=dt, air_density_kg_m3=0.0)
@@ -122,0 +125 @@ def test_zero_gravity_powered_then_coast_limit() -> None:
+        air_density_kg_m3=0.0,
@@ -138,0 +142 @@ def test_zero_force_preserves_uniform_motion() -> None:
+        air_density_kg_m3=0.0,
diff --git a/tests/test_config.py b/tests/test_config.py
index 4f56fa3..d1fe59b 100644
--- a/tests/test_config.py
+++ b/tests/test_config.py
@@ -9 +9,8 @@ def test_zero_valued_limiting_parameters_are_valid() -> None:
-    config = SimulationConfig(thrust_n=0.0, burn_time_s=0.0, gravity_m_s2=0.0)
+    config = SimulationConfig(
+        thrust_n=0.0,
+        burn_time_s=0.0,
+        gravity_m_s2=0.0,
+        air_density_kg_m3=0.0,
+        drag_coefficient=0.0,
+        reference_area_m2=0.0,
+    )
@@ -13,0 +21,11 @@ def test_zero_valued_limiting_parameters_are_valid() -> None:
+    assert config.air_density_kg_m3 == 0.0
+    assert config.drag_coefficient == 0.0
+    assert config.reference_area_m2 == 0.0
+
+
+def test_default_aerodynamic_values_are_documented_educational_constants() -> None:
+    config = SimulationConfig()
+
+    assert config.air_density_kg_m3 == 1.225
+    assert config.drag_coefficient == 0.75
+    assert config.reference_area_m2 == 0.01
@@ -25,0 +44,3 @@ def test_zero_valued_limiting_parameters_are_valid() -> None:
+        ("air_density_kg_m3", -1.0),
+        ("drag_coefficient", -1.0),
+        ("reference_area_m2", -1.0),
@@ -41,0 +63,3 @@ def test_invalid_physical_ranges_are_rejected(field: str, value: float) -> None:
+        "air_density_kg_m3",
+        "drag_coefficient",
+        "reference_area_m2",
diff --git a/tests/test_convergence.py b/tests/test_convergence.py
index 070a219..dfed43d 100644
--- a/tests/test_convergence.py
+++ b/tests/test_convergence.py
@@ -16,0 +17 @@ def _powered_position_error(dt: float) -> float:
+            air_density_kg_m3=0.0,
@@ -38 +39,3 @@ def _default_landing_time_error(dt: float, analytical_time_s: float) -> float:
-    simulation = Simulation(SimulationConfig(physics_dt_s=dt))
+    simulation = Simulation(
+        SimulationConfig(physics_dt_s=dt, air_density_kg_m3=0.0)
+    )
diff --git a/tests/test_drag_validation.py b/tests/test_drag_validation.py
new file mode 100644
index 0000000..56b7f6c
--- /dev/null
+++ b/tests/test_drag_validation.py
@@ -0,0 +1,177 @@
+import math
+
+import pytest
+
+from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
+from rocket_sim.physics import force_breakdown_n
+
+
+def _run_vertical_fall(dt: float) -> Simulation:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=2.0,
+            thrust_n=0.0,
+            burn_time_s=0.0,
+            gravity_m_s2=8.0,
+            air_density_kg_m3=2.0,
+            drag_coefficient=1.0,
+            reference_area_m2=1.0,
+            physics_dt_s=dt,
+            initial_position_m=Vector2(0.0, 100.0),
+            initial_velocity_m_s=Vector2(0.0, 0.0),
+        )
+    )
+    simulation.launch()
+    for _ in range(round(1.0 / dt)):
+        assert simulation.step()
+    return simulation
+
+
+def _vertical_fall_errors(dt: float) -> tuple[float, float]:
+    simulation = _run_vertical_fall(dt)
+    terminal_speed_m_s = 4.0
+    expected_velocity_m_s = -terminal_speed_m_s * math.tanh(2.0)
+    expected_altitude_m = 100.0 - 2.0 * math.log(math.cosh(2.0))
+    return (
+        abs(simulation.state.velocity_m_s.y - expected_velocity_m_s),
+        abs(simulation.state.position_m.y - expected_altitude_m),
+    )
+
+
+def test_vertical_drag_fall_matches_independent_closed_form_reference() -> None:
+    simulation = _run_vertical_fall(0.005)
+    expected_velocity_m_s = -4.0 * math.tanh(2.0)
+    expected_altitude_m = 100.0 - 2.0 * math.log(math.cosh(2.0))
+
+    assert simulation.state.time_s == pytest.approx(1.0, abs=1e-12)
+    assert simulation.state.velocity_m_s.y == pytest.approx(
+        expected_velocity_m_s, abs=0.004
+    )
+    assert simulation.state.position_m.y == pytest.approx(
+        expected_altitude_m, abs=0.015
+    )
+    assert simulation.state.phase is FlightPhase.COAST
+    assert simulation.state.position_m.y > 90.0
+
+
+def test_vertical_drag_fall_exhibits_measured_first_order_convergence() -> None:
+    errors = [_vertical_fall_errors(dt) for dt in (0.02, 0.01, 0.005)]
+    velocity_errors = [error[0] for error in errors]
+    altitude_errors = [error[1] for error in errors]
+
+    assert velocity_errors[0] > velocity_errors[1] > velocity_errors[2]
+    assert altitude_errors[0] > altitude_errors[1] > altitude_errors[2]
+    assert 1.8 < velocity_errors[0] / velocity_errors[1] < 2.2
+    assert 1.8 < velocity_errors[1] / velocity_errors[2] < 2.2
+    assert 1.8 < altitude_errors[0] / altitude_errors[1] < 2.2
+    assert 1.8 < altitude_errors[1] / altitude_errors[2] < 2.2
+
+
+@pytest.mark.parametrize(
+    ("field", "value"),
+    [
+        ("air_density_kg_m3", 0.0),
+        ("drag_coefficient", 0.0),
+        ("reference_area_m2", 0.0),
+    ],
+)
+def test_each_zero_aerodynamic_parameter_recovers_prompt_02_motion(
+    field: str, value: float
+) -> None:
+    parameters = {
+        "mass_kg": 2.0,
+        "thrust_n": 12.0,
+        "burn_time_s": 2.0,
+        "launch_angle_rad": math.radians(30.0),
+        "gravity_m_s2": 3.0,
+        "air_density_kg_m3": 2.0,
+        "drag_coefficient": 0.5,
+        "reference_area_m2": 0.25,
+        "physics_dt_s": 0.01,
+        "initial_position_m": Vector2(0.0, 10.0),
+        "initial_velocity_m_s": Vector2(1.0, 2.0),
+    }
+    parameters[field] = value
+    simulation = Simulation(SimulationConfig(**parameters))
+    simulation.launch()
+    for _ in range(50):
+        assert simulation.step()
+
+    ax = 12.0 * math.cos(math.radians(30.0)) / 2.0
+    ay = 12.0 * math.sin(math.radians(30.0)) / 2.0 - 3.0
+    expected_vx = 1.0 + ax * 0.5
+    expected_vy = 2.0 + ay * 0.5
+    expected_x = 0.5 + 0.5 * ax * 0.5**2 + 0.5 * ax * 0.5 * 0.01
+    expected_y = (
+        10.0
+        + 2.0 * 0.5
+        + 0.5 * ay * 0.5**2
+        + 0.5 * ay * 0.5 * 0.01
+    )
+
+    assert simulation.state.velocity_m_s.x == pytest.approx(expected_vx, abs=1e-12)
+    assert simulation.state.velocity_m_s.y == pytest.approx(expected_vy, abs=1e-12)
+    assert simulation.state.position_m.x == pytest.approx(expected_x, abs=1e-12)
+    assert simulation.state.position_m.y == pytest.approx(expected_y, abs=1e-12)
+
+
+def test_drag_directions_are_coherent_through_default_flight() -> None:
+    simulation = Simulation()
+    simulation.launch()
+    powered_ascent = None
+    coast_ascent = None
+    descent = None
+
+    for _ in range(1000):
+        state = simulation.state
+        if state.velocity_m_s.y > 0.0:
+            if state.phase is FlightPhase.POWERED and powered_ascent is None:
+                powered_ascent = state
+            if state.phase is FlightPhase.COAST and coast_ascent is None:
+                coast_ascent = state
+        elif state.velocity_m_s.y < 0.0 and state.phase is FlightPhase.COAST:
+            descent = state
+            break
+        if not simulation.step():
+            break
+
+    assert powered_ascent is not None
+    assert coast_ascent is not None
+    assert descent is not None
+
+    powered_forces = force_breakdown_n(
+        simulation.config, powered_ascent.time_s, powered_ascent.velocity_m_s
+    )
+    coast_forces = force_breakdown_n(
+        simulation.config, coast_ascent.time_s, coast_ascent.velocity_m_s
+    )
+    descent_forces = force_breakdown_n(
+        simulation.config, descent.time_s, descent.velocity_m_s
+    )
+
+    assert powered_forces.thrust_n.y > 0.0
+    assert powered_forces.gravity_n.y < 0.0
+    assert powered_forces.drag_n.y < 0.0
+    assert coast_forces.thrust_n == Vector2(0.0, 0.0)
+    assert coast_forces.gravity_n.y < 0.0
+    assert coast_forces.drag_n.y < 0.0
+    assert descent_forces.thrust_n == Vector2(0.0, 0.0)
+    assert descent_forces.gravity_n.y < 0.0
+    assert descent_forces.drag_n.y > 0.0
+    assert {sample.mass_kg for sample in simulation.trajectory} == {1.0}
+
+
+def test_active_drag_reduces_apogee_from_zero_drag_limit() -> None:
+    with_drag = Simulation()
+    without_drag = Simulation(SimulationConfig(air_density_kg_m3=0.0))
+
+    for simulation in (with_drag, without_drag):
+        simulation.launch()
+        for _ in range(1000):
+            if simulation.state.velocity_m_s.y < 0.0:
+                break
+            assert simulation.step()
+
+    drag_apogee = max(sample.position_m.y for sample in with_drag.trajectory)
+    vacuum_apogee = max(sample.position_m.y for sample in without_drag.trajectory)
+    assert drag_apogee < vacuum_apogee
diff --git a/tests/test_forces.py b/tests/test_forces.py
index 40da991..470ed97 100644
--- a/tests/test_forces.py
+++ b/tests/test_forces.py
@@ -5 +5 @@ import pytest
-from rocket_sim import SimulationConfig
+from rocket_sim import SimulationConfig, Vector2
@@ -45 +45 @@ def test_net_acceleration_is_force_sum_divided_by_mass() -> None:
-    acceleration = acceleration_m_s2(config, 0.25)
+    acceleration = acceleration_m_s2(config, 0.25, Vector2(0.0, 0.0))
diff --git a/tests/test_integrator.py b/tests/test_integrator.py
index 9c2d716..8bfc257 100644
--- a/tests/test_integrator.py
+++ b/tests/test_integrator.py
@@ -0,0 +1,2 @@
+import math
+
@@ -25,0 +28 @@ def test_step_crossing_burnout_is_split_at_exact_boundary() -> None:
+        air_density_kg_m3=0.0,
@@ -63,0 +67,79 @@ def test_mass_is_constant_across_powered_coast_and_landing_states() -> None:
+
+
+def test_drag_step_uses_start_velocity_then_updated_velocity_for_position() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=2.0,
+            thrust_n=10.0,
+            burn_time_s=2.0,
+            launch_angle_rad=0.0,
+            gravity_m_s2=3.0,
+            air_density_kg_m3=2.0,
+            drag_coefficient=0.5,
+            reference_area_m2=0.25,
+            physics_dt_s=0.1,
+            initial_position_m=Vector2(1.0, 10.0),
+            initial_velocity_m_s=Vector2(3.0, 4.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    assert simulation.state.velocity_m_s == Vector2(3.40625, 3.575)
+    assert simulation.state.position_m == Vector2(1.340625, 10.3575)
+
+    resulting_speed = math.hypot(3.40625, 3.575)
+    expected_drag_x = -0.125 * resulting_speed * 3.40625
+    expected_drag_y = -0.125 * resulting_speed * 3.575
+    assert simulation.current_forces.drag_n.x == pytest.approx(
+        expected_drag_x, abs=1e-12
+    )
+    assert simulation.current_forces.drag_n.y == pytest.approx(
+        expected_drag_y, abs=1e-12
+    )
+    assert simulation.current_forces.net_n.x == pytest.approx(
+        10.0 + expected_drag_x, abs=1e-12
+    )
+    assert simulation.current_forces.net_n.y == pytest.approx(
+        -6.0 + expected_drag_y, abs=1e-12
+    )
+    assert simulation.state.acceleration_m_s2.x == pytest.approx(
+        (10.0 + expected_drag_x) / 2.0, abs=1e-12
+    )
+    assert simulation.state.acceleration_m_s2.y == pytest.approx(
+        (-6.0 + expected_drag_y) / 2.0, abs=1e-12
+    )
+
+
+def test_drag_is_recomputed_for_coast_substep_at_exact_burnout() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_n=4.0,
+            burn_time_s=0.5,
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=1.0,
+            drag_coefficient=1.0,
+            reference_area_m2=1.0,
+            physics_dt_s=1.0,
+            initial_position_m=Vector2(0.0, 1.0),
+            initial_velocity_m_s=Vector2(1.0, 0.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    burnout_state = next(
+        sample for sample in simulation.trajectory if sample.time_s == 0.5
+    )
+    assert burnout_state.phase is FlightPhase.COAST
+    assert burnout_state.velocity_m_s.x == pytest.approx(2.75, abs=1e-12)
+    assert burnout_state.position_m.x == pytest.approx(1.375, abs=1e-12)
+    assert burnout_state.acceleration_m_s2.x == pytest.approx(-3.78125, abs=1e-12)
+    assert simulation.state.time_s == 1.0
+    assert simulation.state.velocity_m_s.x == pytest.approx(0.859375, abs=1e-12)
+    assert simulation.state.position_m.x == pytest.approx(1.8046875, abs=1e-12)
+    assert sum(sample.time_s == 0.5 for sample in simulation.trajectory) == 1
diff --git a/tests/test_rendering.py b/tests/test_rendering.py
index 5130f21..23e807f 100644
--- a/tests/test_rendering.py
+++ b/tests/test_rendering.py
@@ -3,0 +4 @@ from pathlib import Path
+from unittest.mock import PropertyMock, patch
@@ -10 +11 @@ import pygame
-from rocket_sim import Simulation, Vector2
+from rocket_sim import ForceBreakdown, Simulation, SimulationConfig, Vector2
@@ -12 +13,7 @@ from rocket_sim.app import handle_keydown, run
-from rocket_sim.rendering import Renderer, world_to_screen
+from rocket_sim.rendering import (
+    CONTROL_ROWS,
+    Renderer,
+    force_vector_endpoint,
+    physics_inspector_rows,
+    world_to_screen,
+)
@@ -18,0 +26,9 @@ def test_world_to_screen_inverts_only_vertical_axis() -> None:
+def test_force_vectors_share_one_scale_and_invert_only_vertical_direction() -> None:
+    origin = (100, 200)
+    scale = 5.0
+
+    assert force_vector_endpoint(origin, Vector2(2.0, 0.0), scale) == (110, 200)
+    assert force_vector_endpoint(origin, Vector2(0.0, 2.0), scale) == (100, 190)
+    assert force_vector_endpoint(origin, Vector2(-1.0, -3.0), scale) == (95, 215)
+
+
@@ -22 +38 @@ def test_rendering_does_not_mutate_simulation_state() -> None:
-        surface = pygame.Surface((900, 700))
+        surface = pygame.Surface((1200, 720))
@@ -26,5 +42,20 @@ def test_rendering_does_not_mutate_simulation_state() -> None:
-        before = (simulation.state, simulation.trajectory)
-
-        Renderer().draw(surface, simulation)
-
-        assert (simulation.state, simulation.trajectory) == before
+        simulation.advance_elapsed(0.005)
+        before = (
+            simulation.state,
+            simulation.trajectory,
+            simulation.accumulator_s,
+            simulation.config,
+        )
+        renderer = Renderer()
+
+        renderer.draw(surface, simulation)
+        renderer.toggle_force_vectors()
+        renderer.toggle_inspector()
+        renderer.draw(surface, simulation)
+
+        assert (
+            simulation.state,
+            simulation.trajectory,
+            simulation.accumulator_s,
+            simulation.config,
+        ) == before
@@ -54 +85,52 @@ def test_core_modules_do_not_depend_on_pygame() -> None:
-def test_keyboard_controls_launch_pause_reset_and_exit() -> None:
+def test_renderer_uses_production_force_breakdown_without_drag_reimplementation() -> None:
+    rendering_path = Path(__file__).parents[1] / "src" / "rocket_sim" / "rendering.py"
+    rendering_source = rendering_path.read_text()
+    assert "drag_force_n" not in rendering_source
+    assert "-0.5 *" not in rendering_source
+
+    sentinel = ForceBreakdown(
+        thrust_n=Vector2(11.0, 12.0),
+        gravity_n=Vector2(13.0, 14.0),
+        drag_n=Vector2(15.0, 16.0),
+        net_n=Vector2(17.0, 18.0),
+    )
+    simulation = Simulation()
+    rows = physics_inspector_rows(simulation, sentinel)
+
+    assert any("Thrust" in row and "11.000" in row and "12.000" in row for row in rows)
+    assert any("Gravity" in row and "13.000" in row and "14.000" in row for row in rows)
+    assert any("Drag" in row and "15.000" in row and "16.000" in row for row in rows)
+    assert any("Net" in row and "17.000" in row and "18.000" in row for row in rows)
+
+    pygame.init()
+    try:
+        surface = pygame.Surface((1200, 720))
+        renderer = Renderer()
+        with (
+            patch.object(
+                Simulation,
+                "current_forces",
+                new_callable=PropertyMock,
+                return_value=sentinel,
+            ) as force_property,
+            patch(
+                "rocket_sim.rendering.force_vector_endpoint",
+                wraps=force_vector_endpoint,
+            ) as endpoint_spy,
+        ):
+            renderer.draw(surface, simulation)
+        force_property.assert_called_once_with()
+        assert [call.args[1] for call in endpoint_spy.call_args_list] == [
+            sentinel.thrust_n,
+            sentinel.gravity_n,
+            sentinel.drag_n,
+            sentinel.net_n,
+        ]
+        assert {
+            call.args[2] for call in endpoint_spy.call_args_list
+        } == {renderer.force_pixels_per_newton}
+    finally:
+        pygame.quit()
+
+
+def test_inspector_contains_required_state_parameters_forces_and_equations() -> None:
@@ -55,0 +138,48 @@ def test_keyboard_controls_launch_pause_reset_and_exit() -> None:
+    rows = physics_inspector_rows(simulation, simulation.current_forces)
+    text = "\n".join(rows)
+
+    for required in (
+        "Phase:",
+        "Time:",
+        "Position:",
+        "Velocity:",
+        "Speed:",
+        "Acceleration:",
+        "Mass:",
+        "Thrust",
+        "Gravity",
+        "Drag",
+        "Net",
+        "rho:",
+        "Cd:",
+        "Area:",
+        "Fg = (0, -m g)",
+        "Ft = T(cos(theta), sin(theta))",
+        "Fd = -0.5 rho Cd A |v_air| v_air",
+        "Fnet = Ft + Fg + Fd",
+        "a = Fnet / m",
+        "Still air: v_air = v_rocket",
+        "rho: 1.2250 kg/m^3",
+        "Cd: 0.7500",
+        "Area: 0.0100 m^2",
+    ):
+        assert required in text
+
+    assert "RIGHT" in CONTROL_ROWS[0]
+    assert "F force vectors" in CONTROL_ROWS[1]
+    assert "I Physics Inspector" in CONTROL_ROWS[1]
+
+
+def test_inspector_distinguishes_no_liftoff_from_impact() -> None:
+    simulation = Simulation(
+        SimulationConfig(thrust_n=0.0, burn_time_s=0.0)
+    )
+    simulation.launch()
+    rows = physics_inspector_rows(simulation, simulation.current_forces)
+    text = "\n".join(rows)
+
+    assert simulation.is_finished
+    assert not simulation.state.has_lifted_off
+    assert "NO LIFTOFF / terminal initial state" in text
+    assert "impact state" not in text
+
@@ -57,10 +187,39 @@ def test_keyboard_controls_launch_pause_reset_and_exit() -> None:
-    assert handle_keydown(pygame.K_SPACE, simulation)
-    assert simulation.is_running
-    assert handle_keydown(pygame.K_SPACE, simulation)
-    assert simulation.is_paused
-    assert handle_keydown(pygame.K_SPACE, simulation)
-    assert simulation.is_running
-    assert not simulation.is_paused
-    assert handle_keydown(pygame.K_r, simulation)
-    assert simulation.state.time_s == 0.0
-    assert not handle_keydown(pygame.K_ESCAPE, simulation)
+def test_keyboard_controls_launch_pause_reset_and_exit() -> None:
+    pygame.init()
+    try:
+        simulation = Simulation()
+        renderer = Renderer()
+
+        assert handle_keydown(pygame.K_SPACE, simulation, renderer)
+        assert simulation.is_running
+        assert handle_keydown(pygame.K_SPACE, simulation, renderer)
+        assert simulation.is_paused
+
+        before_steps = simulation.physics_step_count
+        before_time_s = simulation.state.time_s
+        assert handle_keydown(pygame.K_RIGHT, simulation, renderer)
+        assert simulation.is_paused
+        assert simulation.physics_step_count == before_steps + 1
+        assert simulation.state.time_s == before_time_s + simulation.config.physics_dt_s
+
+        assert renderer.show_force_vectors
+        assert renderer.show_inspector
+        state_before_toggles = simulation.state
+        assert handle_keydown(pygame.K_f, simulation, renderer)
+        assert not renderer.show_force_vectors
+        assert handle_keydown(pygame.K_i, simulation, renderer)
+        assert not renderer.show_inspector
+        assert handle_keydown(pygame.K_f, simulation, renderer)
+        assert handle_keydown(pygame.K_i, simulation, renderer)
+        assert renderer.show_force_vectors
+        assert renderer.show_inspector
+        assert simulation.state == state_before_toggles
+
+        assert handle_keydown(pygame.K_SPACE, simulation, renderer)
+        assert simulation.is_running
+        assert not simulation.is_paused
+        assert handle_keydown(pygame.K_r, simulation, renderer)
+        assert simulation.state.time_s == 0.0
+        assert not handle_keydown(pygame.K_ESCAPE, simulation, renderer)
+    finally:
+        pygame.quit()
diff --git a/tests/test_simulation.py b/tests/test_simulation.py
index eff6166..7e0050b 100644
--- a/tests/test_simulation.py
+++ b/tests/test_simulation.py
@@ -36,0 +37 @@ def test_ground_crossing_is_linearly_interpolated_on_discrete_segment() -> None:
+            air_density_kg_m3=0.0,
@@ -57,0 +59 @@ def test_accelerated_ground_crossing_interpolates_impact_velocity() -> None:
+            air_density_kg_m3=0.0,
@@ -124,0 +127 @@ def test_pre_burn_impact_telemetry_keeps_thrust_and_acceleration_consistent() ->
+            air_density_kg_m3=0.0,
@@ -139,0 +143,45 @@ def test_pre_burn_impact_telemetry_keeps_thrust_and_acceleration_consistent() ->
+def test_drag_telemetry_uses_interpolated_impact_velocity() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_n=1.0,
+            burn_time_s=1.0,
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=2.0,
+            drag_coefficient=1.0,
+            reference_area_m2=1.0,
+            physics_dt_s=0.2,
+            initial_position_m=Vector2(0.0, 0.1),
+            initial_velocity_m_s=Vector2(0.0, -1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    expected_velocity = Vector2(0.125, -0.875)
+    expected_speed = math.sqrt(0.125**2 + 0.875**2)
+    expected_drag = Vector2(
+        -expected_speed * 0.125,
+        expected_speed * 0.875,
+    )
+    assert simulation.state.time_s == pytest.approx(0.125, abs=1e-12)
+    assert simulation.state.velocity_m_s.x == pytest.approx(
+        expected_velocity.x, abs=1e-12
+    )
+    assert simulation.state.velocity_m_s.y == pytest.approx(
+        expected_velocity.y, abs=1e-12
+    )
+    assert simulation.current_forces.drag_n.x == pytest.approx(
+        expected_drag.x, abs=1e-12
+    )
+    assert simulation.current_forces.drag_n.y == pytest.approx(
+        expected_drag.y, abs=1e-12
+    )
+    assert simulation.state.acceleration_m_s2 == Vector2(
+        1.0 + expected_drag.x,
+        expected_drag.y,
+    )
+
+
@@ -208,0 +257,61 @@ def test_pre_launch_wall_time_is_ignored_and_pause_can_resume() -> None:
+
+
+def test_paused_single_step_uses_production_path_and_preserves_accumulator() -> None:
+    paused = Simulation()
+    running = Simulation()
+    for simulation in (paused, running):
+        simulation.launch()
+        simulation.advance_elapsed(0.015)
+
+    paused.toggle_pause()
+    before_time_s = paused.state.time_s
+    before_steps = paused.physics_step_count
+    before_accumulator_s = paused.accumulator_s
+
+    assert paused.single_step_paused()
+    assert running.step()
+
+    assert paused.is_paused
+    assert paused.state.time_s == pytest.approx(
+        before_time_s + paused.config.physics_dt_s, abs=1e-15
+    )
+    assert paused.physics_step_count == before_steps + 1
+    assert paused.accumulator_s == before_accumulator_s
+    assert paused.state == running.state
+    assert paused.trajectory == running.trajectory
+
+
+def test_paused_single_step_preserves_burnout_split() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            burn_time_s=0.015,
+            physics_dt_s=0.01,
+            air_density_kg_m3=1.225,
+        )
+    )
+    simulation.launch()
+    assert simulation.step()
+    simulation.toggle_pause()
+
+    assert simulation.single_step_paused()
+
+    assert simulation.is_paused
+    assert simulation.physics_step_count == 2
+    assert simulation.state.time_s == pytest.approx(0.02, abs=1e-15)
+    assert sum(sample.time_s == 0.015 for sample in simulation.trajectory) == 1
+    assert simulation.state.phase is FlightPhase.COAST
+
+
+def test_paused_single_step_is_inactive_when_not_paused_live_flight() -> None:
+    ready = Simulation()
+    assert not ready.single_step_paused()
+
+    ready.launch()
+    assert not ready.single_step_paused()
+
+    landed = Simulation(
+        SimulationConfig(thrust_n=0.0, burn_time_s=0.0)
+    )
+    landed.launch()
+    assert landed.is_finished
+    assert not landed.single_step_paused()
diff --git a/tests/test_time_accumulator.py b/tests/test_time_accumulator.py
index c6858cb..5b60517 100644
--- a/tests/test_time_accumulator.py
+++ b/tests/test_time_accumulator.py
@@ -8,2 +8,14 @@ from rocket_sim import Simulation, SimulationConfig
-def _run_partitioned(total_s: float, fps: int) -> Simulation:
-    simulation = Simulation()
+def _run_partitioned(
+    total_s: float,
+    fps: int,
+    air_density_kg_m3: float,
+    physics_dt_s: float = 0.01,
+    burn_time_s: float = 1.0,
+) -> Simulation:
+    simulation = Simulation(
+        SimulationConfig(
+            air_density_kg_m3=air_density_kg_m3,
+            physics_dt_s=physics_dt_s,
+            burn_time_s=burn_time_s,
+        )
+    )
@@ -21 +33 @@ def test_fixed_physics_results_are_independent_of_30_60_144_fps_partitions() ->
-    simulations = [_run_partitioned(0.5, fps) for fps in (30, 60, 144)]
+    simulations = [_run_partitioned(0.5, fps, 0.0) for fps in (30, 60, 144)]
@@ -33,0 +46,23 @@ def test_fixed_physics_results_are_independent_of_30_60_144_fps_partitions() ->
+def test_active_drag_results_are_independent_of_30_60_144_fps_partitions() -> None:
+    simulations = [
+        _run_partitioned(
+            0.5,
+            fps,
+            1.225,
+            physics_dt_s=0.125,
+            burn_time_s=0.25,
+        )
+        for fps in (30, 60, 144)
+    ]
+
+    for simulation in simulations:
+        assert simulation.physics_step_count == 4
+        assert simulation.state.time_s == pytest.approx(0.5, abs=1e-12)
+    assert simulations[0].state == simulations[1].state == simulations[2].state
+    assert (
+        simulations[0].trajectory
+        == simulations[1].trajectory
+        == simulations[2].trajectory
+    )
+
+
~~~~~~
