# Prompt 04 — Sampled motor thrust curves and Living Rocketry Course

- Prompt ID: 04
- Recorded: 2026-08-29T13:19:57-07:00
- Starting commit: `c9e1c17ce3ce80d3850b36ecf9d1b978e1d54235`
- Implementation commit: `9cd39497240ad52ffa42a6e55e30f8fd82bc75b0`
- Implementation parent: `c9e1c17ce3ce80d3850b36ecf9d1b978e1d54235`
- Exact zero-context implementation-diff SHA-256: `35f2de6353a836394036dd5cb3b079193e58dfc4247b0ea009c8a25f22da92f0`
- Scope: sampled propulsion, motor timeline, scientific validation, persistent reviewers, and Living Rocketry Course

## Context and constraints

Prompt 04 began from the clean, pushed Prompt 03 state. It was interrupted several times by Codex/Work usage limits, so execution resumed from the exact repository state each time without restarting or discarding valid work. The parent agent retained sole write authority; specialist agents were read-only. Work stayed within Prompt 04: constant rocket mass, fixed world thrust direction, constant gravity, stationary constant-density air, quadratic drag, fixed outer timestep, and the established deterministic ground-event model.

Explicitly excluded were variable mass, propellant depletion, specific impulse, measured-motor import, motor databases or networking, wind, altitude-dependent atmosphere, rotation or stability, recovery, guidance/control, and Prompt 05 work.

## Persistent specialist setup

Prompt 04 added and TOML-validated two project-scoped read-only specialist definitions:

- `.codex/agents/propulsion_reviewer.toml`
- `.codex/agents/learning_reviewer.toml`

All six reviewer definitions—physics, numerical, test, aerodynamics, propulsion, and learning—were validated with Python `tomllib`. They use `sandbox_mode = "read-only"`, `model_reasoning_effort = "high"`, and no pinned model. The new reviewer definitions were successfully invoked through named read-only delegated reviews; where the live runtime could not hot-load a new custom role, the same checked-in definition was supplied to a named delegated reviewer without granting write authority.

## Pre-implementation findings and reconciliation

The propulsion, physics, numerical, test, learning, and focused aerodynamics reviewers independently examined the proposed milestone before implementation. Their findings were reconciled into this contract:

- one immutable, defensively owned `ThrustCurve` is the propulsion source of truth;
- samples begin at exactly `t=0`, later times are strictly increasing, and thrust is finite and non-negative;
- instantaneous thrust is piecewise-linear on the half-open burn interval and zero before ignition and at/after burn end;
- a nonzero final stored sample is the left-limit endpoint of the last trapezoid, while public instantaneous thrust at exact burnout remains zero;
- total, delivered, and interval impulse use exact trapezoidal geometry;
- every fixed outer step is split at each strictly crossed thrust knot;
- each internal segment applies exact thrust impulse once, plus gravity and drag evaluated from the segment-start velocity;
- velocity is updated before position, preserving the accepted semi-implicit rule;
- outer accumulator time and physics-step counting remain independent of rendering FPS;
- current force and acceleration telemetry is recomputed at the resulting time and velocity;
- mass and thrust direction remain constant;
- existing Decision 03 linear interpolation of the first discrete ground crossing remains authoritative;
- exact motor impulse does not make position, drag impulse, apogee, or impact exact; and
- the default curve is synthetic educational data, not a real measured or certified motor.

## Ignition blocker and adjusted default

The initially proposed zero-at-ignition ground default was:

```text
(0.00 s,  0 N)
(0.05 s, 28 N)
(0.12 s, 24 N)
(0.35 s, 20 N)
(0.70 s, 16 N)
(0.95 s,  8 N)
(1.05 s,  0 N)
```

Its first `0.01 s` delivers only `0.028 N*s`, while the default `1 kg` rocket receives `0.0981 N*s` of downward gravity impulse. With no pad, rail, normal-force, hold-down, clamp, or look-ahead support model, that configuration cannot leave the ground in the first free-flight step.

The scientifically narrow resolution was to use this launchable synthetic ground default:

```text
(0.00 s, 12 N)
(0.05 s, 28 N)
(0.12 s, 24 N)
(0.35 s, 20 N)
(0.70 s, 16 N)
(0.95 s,  8 N)
(1.05 s,  0 N)
```

Its independently summed metrics are:

```text
burn duration       1.05 s
peak stored thrust  28 N
total impulse       17.58 N*s
average thrust      16.742857142857... N
first 0.01 s impulse 0.136 N*s
first-step vy       0.0379 m/s
first-step y        0.000379 m
```

The original zero-at-ignition curve remains a separate airborne, zero-gravity, zero-drag educational/validation case. It has `17.28 N*s` total impulse and produces `17.28 m/s` final vertical velocity for the constant `1 kg` limiting case.

## Implementation summary

The implementation added:

- immutable `ThrustSample` and `ThrustCurve` domain types;
- validated sample ownership, half-open interpolation, exact total/delivered/interval impulse, constant/zero limiting constructors, and the launchable default curve;
- a single authoritative `SimulationConfig.thrust_curve` replacing independent scalar thrust and burn duration;
- fixed-direction thrust impulse and a semi-implicit impulse segment update;
- internal splitting at every crossed thrust knot and burn end;
- impulse-aware ground launch admission using the first internal segment rather than `T(0)` alone;
- resulting-state force, acceleration, current-thrust, and delivered-impulse telemetry;
- Physics Inspector motor phase, progress, duration, current/stored-peak/average thrust, and delivered/total impulse;
- a production-data motor timeline with samples, current cursor, burnout marker, endpoint clamping label, and generic nonzero terminal left-limit semantics;
- paused single-step updates through the same production path;
- the permanent Living Rocketry Course policy in `AGENTS.md`;
- `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md`, a nine-lesson Predict–Observe–Explain course covering the laboratory, motion, Newton's laws, powered flight, burnout/coast/apogee, drag, terminal velocity, model limitations, and sampled motors/impulse;
- Decision 06 for the Living Course; and
- Decision 07 for the sampled thrust-curve model, including its narrow partial supersession of Decision 02 propulsion provisions.

## Post-implementation specialist findings and resolutions

All specialists remained read-only. The parent agent implemented every accepted correction.

### Propulsion reviewer

Initial result: no BLOCKING finding. It identified that a generic nonzero final stored sample is a left-limit ordinate and that “peak” is therefore the maximum stored ordinate / represented-curve supremum. It also found Decision 07 needed to acknowledge partial supersession of Decision 02's propulsion representation.

Resolution: documentation and UI now say “stored peak”; generic nonzero terminal samples render as an open left-limit point plus a filled zero-thrust point at exact burnout; the zero-duration Inspector explicitly says no burn; Decision 02 and Decision 07 link the narrow partial supersession; course peak-marker wording was corrected. Final-resolution review: PASS, no BLOCKING or IMPORTANT findings.

### Physics reviewer

Initial result: no BLOCKING finding. It noted that linearly interpolated powered-impact velocity need not equal exact partial curve impulse at the reported time when thrust varies.

Resolution: the parent did not introduce a new impact root solver, because that would silently supersede the accepted Prompt 02/03 Decision 03 event contract and expand Prompt 04 scope. The limitation remains explicit. A literal rising-thrust powered-impact regression now proves the intended contract: reported `t=0.1 s`, `x=0.056 m`, interpolated `vx=0.28 m/s`, current thrust `2.8 N`, and delivered impulse `0.24 N*s`. Final-resolution physics review: PASS, no BLOCKING or IMPORTANT findings.

### Numerical reviewer

Result: no BLOCKING finding. It verified exact prefix/partial impulse, strict knot splitting, one outer-step count, start-state drag, no thrust double counting, semi-implicit ordering, resulting-state telemetry, nonaligned burnout, active-drag knot recomputation, independent RK4 convergence, FPS independence, reset, and paused stepping. Its IMPORTANT documentation finding—provisional suite wording—was resolved with the final `162 passed` result. Final gate: PASS.

### Test reviewer

The review caught and prevented a temporary unauthorized impact-root change, preserving Decision 03. It requested explicit evidence for time-varying powered-impact telemetry and for impulse-aware ground admission when `T(0)=0` but the first finite interval has sufficient impulse. Both literal regressions were added. It refreshed and executed the current course heredocs after retracting an observation based on an older in-turn snapshot. Final-resolution review: PASS, no BLOCKING or IMPORTANT findings.

### Learning reviewer

Initial result: no scientific BLOCKING finding. It requested clearer overlay-state guidance, momentum and notation scaffolding, honest peak-marker wording, READY-current-thrust explanation, precise default burnout language, positive-parameter conditions for terminal velocity, redundant-knot mesh limitations, and final validation wording.

Resolution: all nine course corrections were integrated and re-reviewed. Final learning gate: PASS, no BLOCKING or IMPORTANT findings. Both headless course activities execute with their documented values.

### Aerodynamics reviewer

Result: no BLOCKING or IMPORTANT finding. It confirmed the constant-property still-air quadratic-drag contract, signs, units, start-of-segment evaluation, knot-boundary recomputation, no duplicate force, limiting cases, convergence, terminal velocity, and renderer sourcing. Its optional wording clarification—that integration uses exact thrust impulse plus shared gravity/drag helpers while presentation consumes instantaneous `ForceBreakdown`—was applied. Final gate: PASS.

## Validation evidence

Environment provenance:

```text
Python 3.12.14
/Users/eugenelin/.conda/envs/rocketsim/bin/python
pip 26.2.1 from the rocketsim Conda environment
```

Final automated validation:

```text
162 passed in 0.62 s
compileall: passed
package import: passed
bounded dummy SDL application, 3 frames: passed
git diff --check: passed
```

Focused results:

```text
propulsion unit tests                         28 passed
propulsion integration and validation        14 passed
force/integrator/analytical/drag regression 45 passed
lifecycle/accumulator/rendering              38 passed
```

Independent sampled-thrust active-drag RK4 reference at `t=0.6 s`:

```text
position = (2.086955589988, 100.340594347210) m
velocity = (4.360834957988, -0.023157593980) m/s
```

| `dt` (s) | position-vector error (m) | velocity-vector error (m/s) |
| ---: | ---: | ---: |
| 0.020 | 0.0261762225 | 0.0046348364 |
| 0.010 | 0.0136805265 | 0.0024161277 |
| 0.005 | 0.0068400396 | 0.0012071078 |

Position-error ratios are approximately `1.913` and `2.000`; velocity-error ratios are approximately `1.918` and `2.002`, consistent with first-order convergence for the selected stable case. Propulsion-only final velocity agrees with exact impulse to roundoff at all tested timesteps.

The terminal-velocity course activity produced:

```text
simulated vy: -3.8598482081396686 m/s
analytical vy: -3.8561103203032676 m/s
terminal-speed magnitude: 4.0 m/s
```

The zero-at-ignition course activity produced:

```text
T(0): 0.0 N
first 0.01 s impulse: 0.028000000000000004 N*s
total impulse: 17.28 N*s
final vertical velocity: 17.28 m/s
```

Sampled-thrust results are identical through the public accumulator for 30, 60, and 144 FPS partitions, including state, trajectory, forces, delivered impulse, step count, and residue. Reset/rerun is deterministic. Single stepping while paused uses the production knot-crossing path and remains paused.

Automated UI evidence verifies one common force-arrow scale, exact production force-vector sourcing, Inspector rows and equations, production-curve identity at the timeline, cursor clamping, generic terminal left-limit semantics, zero-duration status, keyboard controls, and renderer non-mutation. Production frames were visually inspected at powered ascent, declining thrust, burnout, coast, and paused single-step states. A final default frame at `t=0.500 s` displayed `18.286 N` current thrust and `10.751 N*s` delivered impulse; a rectangular limiting curve displayed the open nonzero left limit and exact-burnout zero point.

## Files created

- `.codex/agents/learning_reviewer.toml`
- `.codex/agents/propulsion_reviewer.toml`
- `docs/decisions/decision_06_living_rocketry_course.md`
- `docs/decisions/decision_07_sampled_thrust_curve_model.md`
- `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md`
- `src/rocket_sim/propulsion.py`
- `tests/test_propulsion.py`
- `tests/test_propulsion_integration.py`
- `tests/test_propulsion_validation.py`

## Files modified

- `AGENTS.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/MILESTONES.md`
- `docs/PHYSICS_MODEL.md`
- `docs/RESEARCH_LOG.md`
- `docs/VALIDATION.md`
- `docs/decisions/decision_02_constant_thrust_state_model.md`
- `docs/product/PROJECT_UNDERSTANDING.md`
- `src/rocket_sim/__init__.py`
- `src/rocket_sim/app.py`
- `src/rocket_sim/config.py`
- `src/rocket_sim/physics.py`
- `src/rocket_sim/rendering.py`
- `src/rocket_sim/simulation.py`
- `tests/test_aerodynamics.py`
- `tests/test_analytical_validation.py`
- `tests/test_config.py`
- `tests/test_convergence.py`
- `tests/test_drag_validation.py`
- `tests/test_forces.py`
- `tests/test_integrator.py`
- `tests/test_rendering.py`
- `tests/test_simulation.py`
- `tests/test_time_accumulator.py`

No files were deleted.

## Original Prompt 04 (verbatim)

~~~~~~~text
# Prompt 04 — Sampled Motor Thrust Curves, Impulse, Motor Timeline, and Living Rocketry Course

Work in:

```text
/Users/eugenelin/dev/cwsf2027/rocketsim
```

Canonical repository:

```text
https://github.com/eugenelin89/rocketsim.git
```

This is **Prompt 04**.

Prompt 03 completed:

* constant-mass 2D point-flight dynamics;
* constant gravity;
* finite-duration fixed-direction thrust;
* constant-property quadratic aerodynamic drag in still air;
* fixed-timestep numerical integration;
* exact burnout/event handling;
* analytical and convergence validation;
* persistent scientific specialist review;
* a shared production `ForceBreakdown`;
* a Physics Inspector;
* force-vector visualization;
* paused single-step mode;
* educational phase visualization.

Prompt 04 has two tightly related goals.

## Goal A — Add one new propulsion model

Replace the idealized rectangular constant-thrust burn with an explicitly sampled, time-varying thrust curve:

> **The rocket motor shall produce thrust `T(t)` from a validated piecewise-linear sampled thrust curve while rocket mass remains constant.**

The only new physical effect is **time-varying thrust magnitude**.

Do not add propellant depletion or variable mass yet.

## Goal B — Establish the permanent Living Rocketry Course

Create and institutionalize a tutorial-style learning course that uses RocketSim as an interactive laboratory.

The course must:

* teach the physics currently implemented in RocketSim;
* evolve whenever future validated physics is added or materially changed;
* clearly distinguish real-world physics from RocketSim's approximation;
* connect equations to the Physics Inspector and hands-on experiments;
* never present future or unimplemented features as if they exist.

This must become a standing repository policy, not merely a Prompt 04 task.

The intended progression is:

```text
validated model
      ↓
observable simulator behavior
      ↓
Physics Inspector / educational visualization
      ↓
guided learner experiment
      ↓
prediction → observation → explanation
      ↓
Living Rocketry Course
```

The parent Codex agent remains the sole primary implementer and integrator.

Specialist agents remain read-only reviewers.

Do not begin Prompt 05.

---

# 1. Required repository inspection

Before editing:

1. Read `AGENTS.md` completely.
2. Read `Pygame_Rocket_Simulator_Project_Context.md`.
3. Read `README.md`.
4. Read:

   * `docs/product/PROJECT_UNDERSTANDING.md`
   * `docs/PHYSICS_MODEL.md`
   * `docs/ARCHITECTURE.md`
   * `docs/MILESTONES.md`
   * `docs/VALIDATION.md`
   * `docs/PROJECT_BRIEF.md`
   * `docs/RESEARCH_LOG.md`
5. Read all accepted decisions.
6. Read Prompt 02 and Prompt 03 records.
7. Inspect all source modules and current tests.
8. Inspect the current `.codex/agents/` definitions.
9. Inspect:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 12
```

10. Confirm:

* worktree is clean;
* current branch is `main`;
* `main` tracks `origin/main`;
* local and upstream state agree.

11. Determine the next unused Prompt and Decision IDs.

If repository state conflicts materially with this prompt, stop and report the precise conflict rather than absorbing or discarding unrelated work.

---

# 2. Python environment

Continue using the established primary environment:

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

Do not use:

* Conda `base`;
* Homebrew Python;
* system Python;
* user-global Python.

Do not add NumPy, SciPy, pandas, matplotlib, or a new dependency manager.

Use Python standard library, Pygame, and pytest unless the existing project explicitly requires otherwise.

---

# 3. Preserve all validated Prompt 02–03 behavior

Prompt 04 must preserve:

* SI units;
* +x right / +y upward;
* constant rocket mass;
* gravity semantics;
* fixed thrust direction in world coordinates;
* quadratic drag;
* still-air semantics;
* aerodynamic configuration;
* exact drag direction and `v²` behavior;
* fixed-step wall-time separation;
* compensated accumulator;
* deterministic reset;
* liftoff semantics;
* ground-return semantics;
* rendering/physics separation;
* Physics Inspector;
* force-vector sourcing from production physics;
* paused single-step behavior;
* FPS independence.

With a constant thrust curve equivalent to the previous constant-thrust model, Prompt 04 must reproduce Prompt 03 physical behavior within established floating-point semantics.

Do not silently change a validated earlier contract.

---

# 4. Prompt 04 physical scope

Add only:

* immutable sampled thrust data;
* piecewise-linear thrust interpolation;
* time-varying thrust magnitude `T(t)`;
* burn duration derived from the thrust curve;
* total impulse;
* delivered impulse as a function of time;
* average thrust;
* peak thrust;
* propulsion timeline visualization;
* corresponding scientific validation.

Rocket mass remains constant.

Thrust direction remains fixed.

---

# 5. Explicit physical non-goals

Do not implement:

* variable mass;
* dry mass;
* propellant mass;
* mass flow;
* propellant depletion;
* the Tsiolkovsky rocket equation;
* chamber pressure;
* nozzle geometry;
* specific impulse;
* exhaust velocity;
* motor thermochemistry;
* ignition chemistry;
* real combustion simulation;
* thrust-vector control;
* changing thrust direction;
* wind;
* altitude-varying atmosphere;
* temperature or pressure atmosphere;
* Mach effects;
* Reynolds-number effects;
* variable `Cd`;
* lift;
* rotation;
* torque;
* CG/CP;
* stability;
* recovery;
* parachutes;
* guidance;
* control;
* optimization;
* Monte Carlo;
* CSV experiment export;
* parameter sweeps;
* multiple rockets;
* swarm behavior.

Do not create speculative subsystem frameworks for these features.

---

# 6. External motor-data scope

Prompt 04 should implement the **scientific model for sampled thrust curves**, not a general motor-data ecosystem.

Do not add:

* arbitrary online downloads;
* motor databases;
* network access;
* vendor APIs;
* ThrustCurve.org integration;
* RASP/ENG file import unless an existing repository requirement specifically justifies it;
* general file browsers or motor-selection GUIs.

Use a documented bundled **synthetic educational thrust curve** as the default.

Clearly state that the default curve is educational and is **not measured data from a real certified motor**.

The architecture should allow future validated real-motor data ingestion without requiring it now.

Do not call synthetic data “real motor data.”

---

# 7. Add persistent `propulsion_reviewer`

Create:

```text
.codex/agents/propulsion_reviewer.toml
```

Use the established project-agent schema.

It should be equivalent to:

```toml
name = "propulsion_reviewer"
description = "Independently reviews RocketSim thrust-curve semantics, interpolation, impulse, burn timing, motor metrics, propulsion assumptions, and propulsion validation."

sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
You are RocketSim's independent propulsion reviewer.

You are a reviewer, not an implementation agent.

Do not modify repository files.

Your primary question is:

Does the implementation correctly represent the documented sampled
time-varying thrust model?

Review:
- thrust as a function of time
- sampled thrust data
- piecewise-linear interpolation
- sample-boundary behavior
- ignition-time semantics
- burn-end semantics
- thrust before, at, and after burn
- total impulse
- delivered impulse
- average thrust
- peak thrust
- thrust-vector magnitude and fixed direction
- units and dimensional consistency
- constant-thrust limiting behavior
- zero-thrust limiting behavior
- numerical integration of time-varying thrust
- interaction with drag and gravity
- educational motor metrics
- claims about real motors versus synthetic educational data

For Prompt 04, rocket mass remains constant.

Do not introduce:
- propellant depletion
- variable mass
- specific impulse
- exhaust velocity
- chamber pressure
- nozzle design
- motor chemistry
- thrust-vector control

Derive expected values independently rather than copying production helpers.

Classify meaningful findings as:

BLOCKING
IMPORTANT
OPTIONAL

For every meaningful finding:
- explain the propulsion issue;
- reference exact files/functions/tests/equations;
- state expected behavior;
- recommend the smallest scientifically defensible correction.

Do not modify files.
"""
```

Validate with Python 3.12 `tomllib`.

If the runtime cannot hot-load it as a custom project agent, use Decision 04's documented read-only delegated fallback and record that honestly.

---

# 8. Add persistent `learning_reviewer`

Create:

```text
.codex/agents/learning_reviewer.toml
```

This role exists because educational documentation is now a permanent product requirement.

Use a definition equivalent to:

```toml
name = "learning_reviewer"
description = "Independently reviews RocketSim's living rocketry course for scientific consistency, pedagogical clarity, implemented-only claims, guided experiments, and synchronization with the simulator."

sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
You are RocketSim's independent learning-course reviewer.

You are a reviewer, not an implementation agent.

Do not modify repository files.

RocketSim is both a scientifically inspectable simulator and an interactive
environment for learning rocketry.

Your primary question is:

Does the Living Rocketry Course accurately and clearly teach the validated
physics that the current simulator actually implements?

Review:
- consistency with docs/PHYSICS_MODEL.md
- consistency with docs/VALIDATION.md
- consistency with actual simulator controls and UI
- SI units
- coordinate conventions
- equations
- force directions
- assumptions and limitations
- distinction between real-world physics and RocketSim approximation
- whether future features are incorrectly described as implemented
- guided simulator activities
- prediction / observation / explanation structure
- check-your-understanding questions
- whether an existing lesson became outdated after a new milestone
- whether the tutorial explains why the model is simplified
- whether activities are reproducible with the current simulator

The course should teach concepts progressively and should not merely copy
developer documentation.

For each important issue report:

SCIENTIFIC ISSUE
PEDAGOGICAL ISSUE
SIMULATOR / COURSE MISMATCH
RECOMMENDED CORRECTION

Classify completion-critical findings as BLOCKING.

Do not modify files.
"""
```

Validate the TOML with `tomllib`.

Use the same honest fallback if project agent hot-loading is unavailable.

---

# 9. Update `AGENTS.md` with permanent Living Rocketry Course policy

Add a durable section approximately titled:

```text
## Living Rocketry Course Policy
```

This policy must state that RocketSim is both:

* a scientifically inspectable simulator; and
* an educational environment for learning rocketry.

Maintain:

```text
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
```

as a living tutorial-style course.

The policy must establish that **any approved milestone that adds or materially changes**:

* a physical model;
* a force;
* an equation;
* a propulsion model;
* a numerical interpretation important to understanding the physics;
* a physical event or phase;
* Physics Inspector information;
* an educational visualization;
* a simulator experiment;
* a user-facing control relevant to learning;

must review and, where applicable, update the Living Rocketry Course before the milestone is complete.

Include explicitly:

> The parent agent must not wait for a future prompt to explicitly request a course update.

The course must:

* teach only implemented and validated behavior as currently available;
* clearly distinguish real-world physics from the current RocketSim approximation;
* use the same equations, units, signs, and coordinate conventions as `docs/PHYSICS_MODEL.md`;
* remain consistent with `docs/VALIDATION.md`;
* not present future functionality as implemented;
* connect concepts to hands-on simulator observations and experiments;
* include assumptions and model limitations;
* include prediction → observation → explanation activities where appropriate;
* include check-your-understanding questions;
* revise older lessons when later milestones refine an earlier simplification.

Scientific truth remains in:

```text
docs/PHYSICS_MODEL.md
```

Validation methodology remains in:

```text
docs/VALIDATION.md
```

The learning course pedagogically explains validated behavior; it is not an independent source of physics truth.

Add:

> A physics or educational milestone is not complete until applicable Living Rocketry Course material has been reviewed for consistency.

---

# 10. Update specialist policy in `AGENTS.md`

Add concise invocation policy for:

### `propulsion_reviewer`

Invoke for:

* thrust curves;
* motor burn timing;
* thrust interpolation;
* impulse;
* average/peak thrust;
* propulsion assumptions;
* later motor models.

### `learning_reviewer`

Invoke before completion of any milestone that changes:

* physics;
* propulsion;
* Physics Inspector;
* educational visualization;
* learner controls;
* course content.

Do not duplicate full TOML instructions in `AGENTS.md`.

Preserve read-only authority.

Parent remains sole implementer/integrator.

---

# 11. Pre-implementation specialist review

Before central implementation, invoke:

* `propulsion_reviewer`;
* `physics_reviewer`;
* `numerical_reviewer`;
* `test_reviewer`;
* `learning_reviewer`.

They may run in parallel because they are read-only.

Wait for all five.

Because Prompt 04 changes the numerical stepping path while drag remains active, obtain at least a focused `aerodynamics_reviewer` review of the reconciled numerical plan before implementation or during the post-review gate.

Do not allow specialists to edit files.

---

# 12. Propulsion pre-review

Ask `propulsion_reviewer` to independently determine:

* appropriate sampled-curve representation;
* interpolation semantics;
* exact sample-time semantics;
* burn-start and burn-end behavior;
* total-impulse formula;
* partial/delivered-impulse formula;
* average thrust;
* peak thrust;
* constant-thrust limiting representation;
* zero-thrust representation;
* treatment of a physics step crossing thrust-sample boundaries;
* treatment of the final burn endpoint;
* scientifically defensible numerical integration semantics.

Require independent derivation.

---

# 13. Physics pre-review

Ask `physics_reviewer` to verify:

```text
F_thrust(t) = T(t) u_thrust
```

where:

```text
u_thrust = (cos(theta), sin(theta))
```

and:

```text
F_net =
    F_thrust(t)
    + F_gravity
    + F_drag
```

Require review of:

* units;
* direction;
* changing magnitude;
* powered/coast interpretation;
* exact transition to zero thrust;
* gravity/drag interaction;
* constant mass;
* no hidden new physics.

---

# 14. Numerical pre-review

Time-varying thrust means thrust is no longer generally constant within a full physics timestep.

Ask `numerical_reviewer` to explicitly review whether Prompt 04 should:

1. evaluate thrust only at segment start; or
2. exploit the known piecewise-linear thrust curve to integrate thrust impulse exactly over each internal subsegment.

The preferred scientific design is:

> Split a fixed outer timestep at any thrust-curve sample boundary it crosses and use the exact integral of the piecewise-linear thrust magnitude over each internal segment.

For a segment `[t0,t1]` within one linear thrust interval:

```text
J_thrust =
    integral from t0 to t1 of T(t) dt
```

Because `T(t)` is linear over the segment:

```text
J_thrust =
    0.5 * (T_left + T_right) * (t1 - t0)
```

The thrust impulse vector is:

```text
J_vector = J_thrust * u_thrust
```

The parent and reviewer should confirm the exact numerical contract before implementation.

Do not silently change the earlier integration method without documenting the reason.

---

# 15. Preferred Prompt 04 velocity update

If the numerical review confirms the preferred approach, use:

```text
J_T = exact thrust impulse over the internal segment

F_other_start =
    F_gravity
    + F_drag(v_start)

delta_v =
    J_T / m
    + (F_other_start / m) * dt

v_next =
    v_start + delta_v

p_next =
    p_start + v_next * dt
```

This keeps:

* thrust impulse exact for the piecewise-linear motor representation;
* gravity exact as a constant force;
* drag explicitly evaluated from segment-start velocity;
* semi-implicit position update.

If the reviewer recommends a materially different scheme, document the derivation and rationale before implementation.

Do not move to a general-purpose ODE solver.

---

# 16. Thrust-curve representation

Introduce the smallest Pygame-independent propulsion representation needed.

A structure conceptually like:

```text
ThrustSample
    time_s
    thrust_n

ThrustCurve
    samples
```

is appropriate.

A dedicated module such as:

```text
src/rocket_sim/propulsion.py
```

is reasonable because propulsion is now an active domain.

Do not create a generalized plugin system.

---

# 17. Thrust sample validation

Require:

* sample times finite;
* thrust values finite;
* thrust values non-negative;
* first sample time exactly `0`;
* sample times strictly increasing after the first;
* no duplicate sample times;
* no negative time;
* at least one valid representation of the zero-duration zero-thrust limiting case.

For a normal non-zero-duration curve, require at least two samples.

The final sample time defines the motor burn duration.

Do not infer burn duration from a separate independent scalar.

Avoid multiple competing sources of truth.

---

# 18. Instantaneous thrust semantics

For:

```text
0 <= t < burn_end
```

evaluate thrust by linear interpolation between surrounding samples.

For:

```text
t < 0
```

thrust is zero.

For:

```text
t >= burn_end
```

thrust is zero.

The burn interval remains half-open.

At an interior sample time, instantaneous thrust must equal that exact sample's thrust.

At exact burn end, instantaneous thrust is zero even if the stored final sample's left-limit value is nonzero.

Document this carefully.

---

# 19. Impulse semantics

Define total impulse:

```text
I_total = integral T(t) dt
```

with units:

```text
N*s
```

For a piecewise-linear curve, calculate total impulse exactly from trapezoidal areas:

```text
I_total =
    sum[
        0.5 * (T_i + T_(i+1))
        * (t_(i+1) - t_i)
    ]
```

Do not numerically approximate total impulse using the simulation timestep.

---

# 20. Delivered impulse

Expose a motor quantity equivalent to:

```text
I_delivered(t) =
    integral from 0 to clamp(t, 0, burn_end)
    of T(tau) d tau
```

Compute it from the mathematical thrust curve, not from accumulated simulation timestep samples.

Require:

```text
I_delivered(t < 0) = 0
I_delivered(0) = 0
I_delivered(t >= burn_end) = I_total
```

It must be monotonic for non-negative thrust.

---

# 21. Average and peak thrust

Define:

```text
T_average = I_total / burn_duration
```

for positive burn duration.

Define peak thrust as:

```text
T_peak = max(sample thrust values)
```

because piecewise-linear interpolation cannot exceed the maximum of its endpoint samples.

For a zero-duration no-thrust curve, define average and peak behavior explicitly and safely.

Do not divide by zero.

---

# 22. Constant-thrust limiting curve

Provide a simple factory or constructor for the Prompt 02–03 constant-thrust limit.

Conceptually:

```text
constant T over 0 <= t < burn_time
```

may be represented by:

```text
(0, T)
(burn_time, T)
```

with the half-open burn-end rule setting instantaneous thrust to zero at and after the final time.

Its exact impulse must be:

```text
T * burn_time
```

Use this to establish regression equivalence with Prompt 03.

Avoid preserving obsolete scalar `thrust_n` and `burn_time_s` as a second independent source of propulsion truth unless compatibility absolutely requires it and the design is explicitly reconciled.

Prefer one authoritative motor/thrust representation.

---

# 23. Zero-thrust limiting case

Support a clear zero-thrust curve.

The zero-thrust representation must:

* produce zero instantaneous thrust;
* produce zero delivered impulse;
* produce zero total impulse;
* remain valid in gravity/drag ballistic tests.

Do not special-case physics elsewhere merely to support it.

---

# 24. Default educational thrust curve

Use a deterministic bundled **synthetic educational thrust curve**.

Unless specialist review identifies a compelling reason to adjust it, use approximately:

```text
time_s   thrust_N
0.00      0
0.05     28
0.12     24
0.35     20
0.70     16
0.95      8
1.05      0
```

For this exact curve, the trapezoidal total impulse should be independently verified as:

```text
17.28 N*s
```

Its nominal burn duration is:

```text
1.05 s
```

Peak thrust:

```text
28 N
```

Average thrust:

```text
17.28 / 1.05
≈ 16.4571 N
```

The curve is self-authored educational data.

Do not identify it with a commercial motor.

Document that real motors may have substantially different curve shapes.

---

# 25. Default liftoff sanity

The default educational curve begins at zero thrust but rises rapidly.

Because RocketSim has no launch-rail/contact-support model, review the current ground-admission semantics carefully.

Do not let the zero thrust at exact `t=0` cause an otherwise physically meaningful default curve to be classified immediately as “no liftoff” merely because the current admission logic only samples the instantaneous force at ignition.

This is an important Prompt 04 issue.

The specialists must reconcile the smallest scientifically defensible treatment.

Possible acceptable approaches include evaluating whether the first configured numerical/motor segment develops positive motion under the time-varying thrust curve, without inventing a pad support force.

Do not introduce launch-rail dynamics or a normal-force model.

Document the chosen simplified liftoff semantics and test them independently.

---

# 26. Do not hide the ignition issue

The default sampled curve exposes an important distinction:

```text
instantaneous thrust at ignition = 0
```

does not imply:

```text
the motor produces no impulse over the first finite interval
```

The simulation must correctly account for the increasing thrust over that interval.

This behavior should become an educational example in the Living Rocketry Course.

---

# 27. Exact sample-boundary handling

A fixed outer timestep may cross one or more thrust-curve sample times.

Do not treat an entire fixed step as belonging to one interpolation segment.

Split internally at every crossed thrust sample boundary necessary to preserve the chosen impulse semantics.

Example:

```text
outer step:
0.10 s → 0.20 s

curve knot:
0.12 s

internal:
0.10 → 0.12
0.12 → 0.20
```

If a timestep crosses multiple knots, handle all of them deterministically.

Do not assume sample spacing is larger than the physics timestep.

---

# 28. Burn end

The last thrust-curve sample time defines burn end.

After:

```text
t >= burn_end
```

instantaneous thrust is zero.

The simulator phase should transition cleanly to coast.

There must be exactly one logical powered-to-coast transition.

Do not maintain a separate unrelated burnout time.

---

# 29. Force observability

Extend the existing force path so:

```text
Simulation.current_forces
```

continues to be the production source for:

* thrust;
* gravity;
* drag;
* net force.

The thrust vector shown by the Physics Inspector must use the instantaneous interpolated `T(t)`.

Do not reconstruct the thrust curve independently in the renderer.

---

# 30. Physics Inspector updates

Update the Physics Inspector to reflect the new propulsion model.

At minimum show:

```text
Current thrust
Motor phase
Burn progress
Burn duration
Peak thrust
Average thrust
Delivered impulse
Total impulse
```

Use SI units:

```text
N
s
N*s
```

Continue showing:

* gravity;
* drag;
* net force;
* state;
* acceleration;
* aerodynamic parameters;
* equations.

Update the thrust equation to something equivalent to:

```text
Ft(t) = T(t) (cos(theta), sin(theta))
```

Do not display variable-mass or specific-impulse equations.

---

# 31. Motor / thrust timeline visualization

Add an educational thrust-curve timeline.

It should display:

* time on horizontal axis;
* thrust in newtons on vertical axis;
* the piecewise-linear thrust curve;
* sample points where readable;
* current simulation-time cursor;
* burnout/end marker;
* current thrust;
* peak thrust indication where simple.

The curve displayed must come from the same `ThrustCurve` used by production physics.

Do not maintain separate graph data.

---

# 32. Timeline interaction with paused single-step

When paused and RIGHT ARROW advances one physics timestep:

* the timeline cursor must advance with simulation time;
* current thrust must update accordingly;
* delivered impulse must update;
* force arrows must update;
* the simulation must remain paused.

This should make the relationship visible:

```text
position on thrust curve
        ↓
current thrust
        ↓
net force
        ↓
acceleration
        ↓
change in velocity
```

---

# 33. Timeline rendering ownership

The renderer may:

* choose graph scale;
* draw axes;
* draw samples;
* draw the curve;
* draw the current-time cursor;
* format thrust/impulse values.

The renderer must not:

* calculate a different interpolation model;
* calculate a different impulse model;
* change curve values;
* change simulation time;
* modify physical state.

Use production propulsion data and methods.

---

# 34. No parameter editor yet

Do not add:

* editable thrust samples;
* curve dragging;
* motor file selection;
* motor database browser;
* parameter sliders;
* arbitrary motor authoring UI.

Prompt 04 is an inspectable propulsion model, not a motor-design application.

---

# 35. Required propulsion unit tests

At minimum test independently:

1. valid curve construction;
2. invalid non-finite times;
3. invalid non-finite thrust;
4. negative thrust rejected;
5. negative time rejected where applicable;
6. first sample time requirement;
7. strictly increasing sample time requirement;
8. duplicate time rejection;
9. exact thrust at interior sample points;
10. linear interpolation at known midpoints;
11. thrust zero before ignition;
12. thrust zero at exact burn end;
13. thrust zero after burn end;
14. constant-thrust curve behavior;
15. zero-thrust curve behavior;
16. exact total impulse for a simple triangle;
17. exact total impulse for a rectangle;
18. exact total impulse for a multi-segment curve;
19. delivered impulse inside a segment;
20. delivered impulse across multiple segments;
21. delivered impulse after burn equals total;
22. average thrust;
23. peak thrust;
24. default educational curve metrics.

Expected values must not call production interpolation/impulse helpers to generate their own oracle.

---

# 36. Required default-curve independent metrics

For the proposed educational curve:

```text
(0.00, 0)
(0.05, 28)
(0.12, 24)
(0.35, 20)
(0.70, 16)
(0.95, 8)
(1.05, 0)
```

independently verify:

```text
burn duration = 1.05 s
peak thrust = 28 N
total impulse = 17.28 N*s
average thrust ≈ 16.457142857 N
```

Do not compute expected test values by calling production metrics.

---

# 37. Impulse-momentum validation

Use a high-value independent test with:

```text
gravity = 0
drag = 0
constant mass
fixed thrust direction
```

For total motor impulse `I`:

```text
delta_v_parallel = I / m
```

If the exact piecewise-linear impulse integration approach is adopted, final velocity after burn should agree with this impulse-momentum reference to floating-point precision or an independently justified tolerance.

This is one of the central Prompt 04 scientific validation cases.

---

# 38. Constant-thrust Prompt 03 regression

Construct a constant thrust curve equivalent to the previous default rectangular thrust model.

Run equivalent Prompt 03 configurations using that curve.

Require reproduction of prior:

* thrust;
* burnout;
* velocity;
* position;
* drag interaction;
* landing behavior;
* deterministic reset;
* FPS independence.

Do not weaken earlier tests.

---

# 39. Sample-boundary regression

Create a deliberately awkward case where:

* physics timestep does not align with thrust samples;
* one outer step crosses a sample boundary;
* another case crosses multiple boundaries if feasible.

Independently calculate expected thrust impulse.

Verify no sample segment is skipped or double-counted.

---

# 40. Burn-end regression

Create a curve whose burn end is not aligned to `physics_dt_s`.

Verify:

* exact total delivered motor impulse;
* exactly one burn-end transition;
* zero instantaneous thrust at exact and later burn time;
* coast force/acceleration recomputed appropriately;
* no excess full-step thrust.

---

# 41. Drag interaction

With active drag, verify that:

* thrust varies according to `T(t)`;
* drag remains based on air-relative velocity;
* gravity remains unchanged;
* net force is the correct sum;
* force telemetry at resulting states is current, not stale;
* decreasing motor thrust can change acceleration before burnout even though thrust remains nonzero.

Do not use active drag as the sole propulsion oracle.

---

# 42. Timestep convergence

Use a nontrivial sampled curve and active drag.

Run:

```text
dt = 0.02
dt = 0.01
dt = 0.005
```

Compare a selected state or metric against an independently justified reference.

If exact thrust impulse integration is used, separate:

* propulsion impulse accuracy;
* remaining trajectory error from velocity-dependent drag / position stepping.

Do not claim a convergence order unsupported by measured evidence.

---

# 43. FPS independence

Verify the new time-varying-thrust flight remains identical under equivalent elapsed-time partitions such as:

```text
30 FPS
60 FPS
144 FPS
```

Use the public accumulator path.

Do not bypass it.

---

# 44. Reset determinism

With active sampled thrust and active drag:

* run a nontrivial elapsed-time sequence;
* record state/history/accumulator;
* reset;
* repeat exactly;
* require identical results.

Include motor metrics/time state in the deterministic contract where applicable.

---

# 45. Living Rocketry Course location

Create:

```text
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
```

Create `docs/learning/` if it does not exist.

Begin with one coherent course document.

Do not prematurely split into many chapter files.

If it later becomes unwieldy, a future approved milestone may reorganize it.

---

# 46. Course purpose

The document should read like an interactive introductory rocketry course, not like developer API documentation.

Target a motivated high-school student or beginning undergraduate who is comfortable with basic algebra and is learning mechanics.

Use equations rigorously but explain the physical intuition first.

The simulator is the laboratory.

---

# 47. Course pedagogical pattern

Where appropriate, lessons should use recurring sections such as:

```text
What are we trying to understand?

Physical intuition

Real-world physics

The RocketSim model

Governing equations

What each quantity means

Try it in RocketSim

Predict

Observe

Explain

Model limitations

Check your understanding
```

Do not force every section mechanically when it would make a lesson awkward.

The course should be cohesive rather than templated boilerplate.

---

# 48. Distinguish nature from the model

This is a core course principle.

Use explicit distinctions like:

```text
REAL-WORLD PHYSICS
What happens in nature.

ROCKETSIM MODEL
How the current simulator approximates it.
```

Examples:

* real atmospheric density varies; current RocketSim density is constant;
* real rockets lose propellant mass; current RocketSim mass is constant;
* real rockets rotate; current RocketSim uses fixed thrust direction;
* real `Cd` may depend on Mach and attitude; current RocketSim `Cd` is constant;
* real motor curves come from measurement; Prompt 04's default curve is synthetic educational data.

Do not blur these distinctions.

---

# 49. Backfill the existing course

Prompt 04 must not begin the course at thrust curves.

Create useful lessons for already validated behavior.

At minimum include material approximately covering:

## Part I — Foundations

### 1. RocketSim as a Physics Laboratory

Teach:

* simulator purpose;
* controls;
* Physics Inspector;
* force arrows;
* pause;
* single-step;
* prediction → experiment → explanation.

### 2. Position, Velocity, and Acceleration

Teach:

* +x / +y coordinate system;
* SI units;
* position;
* velocity;
* speed;
* acceleration;
* vectors.

### 3. Forces and Newton's Second Law

Teach:

```text
F_net = sum of forces
a = F_net / m
```

Introduce:

* thrust;
* gravity;
* force vectors;
* net force.

### 4. Powered Flight

Teach:

* thrust versus weight;
* initial acceleration;
* why sufficient upward force is needed;
* current fixed-direction point-mass assumptions.

### 5. Burnout, Coast, and Apogee

Teach:

* thrust becomes zero;
* velocity does not become zero instantly;
* the rocket continues upward after burnout;
* gravity/drag reduce upward velocity;
* apogee.

### 6. Aerodynamic Drag

Teach:

```text
F_drag = -0.5 rho Cd A |v_air| v_air
```

Explain:

* air-relative velocity;
* still air;
* `rho`;
* `Cd`;
* reference area;
* `v²` scaling;
* ascent/descent drag reversal.

### 7. Terminal Velocity

Teach:

* gravity/drag equilibrium;
* zero acceleration does not mean zero velocity;
* analytical terminal-speed relation;
* simulator experiment.

### 8. Current Model Limitations

Explain implemented simplifications honestly.

---

# 50. Add Prompt 04 propulsion lesson

Add a new major lesson approximately:

## 9. Rocket Motors, Thrust Curves, and Impulse

Teach:

* why real motor thrust changes with time;
* thrust curve;
* sampled data;
* interpolation;
* peak thrust;
* average thrust;
* burn duration;
* total impulse;
* delivered impulse;
* area under a thrust-time graph;
* impulse-momentum relationship.

Introduce:

```text
I = integral T(t) dt
```

and:

```text
delta_p = impulse
```

For constant mass in the thrust direction with other forces removed:

```text
delta_v = I / m
```

Clearly state that current RocketSim still keeps mass constant even though real motors consume propellant.

---

# 51. Guided motor experiment

Include a hands-on activity using the new default curve.

For example:

### Predict

Ask the learner:

* When will thrust be largest?
* Is acceleration necessarily largest at exactly the same time?
* Why might drag make the answer different?
* What happens to thrust at burnout?
* What does the area under the thrust curve represent?

### Observe

Have the learner:

1. launch;
2. pause early in the burn;
3. inspect current thrust;
4. inspect the timeline;
5. single-step;
6. watch the cursor move;
7. inspect delivered impulse;
8. compare peak thrust and average thrust;
9. observe burnout.

### Explain

Relate:

```text
thrust curve
→ impulse
→ momentum change
→ velocity
→ drag
→ trajectory
```

---

# 52. Course check-your-understanding questions

Include reasoning questions, not merely definitions.

Examples:

* If thrust becomes zero at burnout, why can the rocket still move upward?
* Why does drag point downward during ascent but upward during descent?
* If speed doubles, how does quadratic drag magnitude change?
* Can acceleration be zero while velocity is nonzero?
* Two motors have the same peak thrust but different total impulse. Must they produce the same velocity change?
* Why can two motors with the same total impulse produce different trajectories when drag is present?
* Why are thrust and impulse different quantities?
* Why does current RocketSim keep mass constant even though real motors do not?

Do not include answer claims unsupported by the implemented model.

---

# 53. Course simulator instructions must be current

Every documented key/control must match the application.

The course should include the actual current controls, including as applicable:

```text
SPACE
RIGHT
R
F
I
ESC
```

and any Prompt 04-specific view behavior.

Do not document controls that do not exist.

---

# 54. Course must evolve retroactively

Because later milestones may refine earlier simplifications, add to repository policy:

> Updating the course may require revising an earlier chapter, not merely appending a new chapter.

Examples:

* when variable mass is added, revisit the powered-flight and motor lessons;
* when atmosphere varies with altitude, revisit drag;
* when wind is added, revisit air-relative velocity;
* when rotation/stability is added, revisit thrust direction and point-mass assumptions.

This principle must be recorded durably.

---

# 55. Living-course scientific review

The `learning_reviewer` must inspect:

* the complete new course;
* all Prompt 02–04 equations taught;
* simulator instructions;
* model limitations;
* guided activities;
* check-your-understanding questions.

Require a direct answer:

> Does the course teach only what the current validated RocketSim can support, while clearly distinguishing real-world rocketry from the simulator approximation?

Any incorrect equation, false implementation claim, or materially misleading model statement is BLOCKING.

---

# 56. Do not test prose with meaningless grep tests

Do not create brittle tests that merely check whether arbitrary tutorial sentences exist as a substitute for scientific review.

Automated tests may check durable machine-readable behavior.

Course correctness should primarily be established through:

* authoritative scientific docs;
* implementation consistency;
* specialist review;
* final documentation audit.

Small targeted documentation-contract checks are acceptable only if they protect a concrete user-facing contract.

---

# 57. Decision records

Inspect actual IDs first.

Prompt 04 is expected to justify approximately two durable decisions.

## Decision approximately 06 — Living Rocketry Course

Record:

* educational product identity;
* permanent course path;
* update requirement;
* relationship among physics docs, validation docs, implementation, and course;
* prediction/observation/explanation philosophy;
* retroactive lesson revision;
* learning-review requirement.

## Decision approximately 07 — Sampled thrust-curve model

Record:

* thrust-curve state representation;
* interpolation;
* burn interval;
* total/delivered impulse;
* numerical integration semantics;
* constant-thrust limiting curve;
* default synthetic curve;
* constant-mass limitation.

Use actual next IDs.

Do not create unnecessary decisions for minor UI details.

---

# 58. Documentation hierarchy

Preserve this hierarchy:

```text
docs/PHYSICS_MODEL.md
    authoritative implemented equations and assumptions

docs/VALIDATION.md
    scientific/numerical evidence

docs/ARCHITECTURE.md
    implementation ownership and boundaries

docs/decisions/
    durable design/scientific choices

docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
    pedagogical explanation and guided learning

README.md
    entry point / discoverability
```

The learning course must not silently become the source of truth for equations.

---

# 59. Update `docs/PHYSICS_MODEL.md`

Document the new propulsion model, including:

```text
T = T(t)

F_T(t) =
    T(t) (cos(theta), sin(theta))
```

Document:

* sampled thrust;
* interpolation;
* burn endpoint;
* impulse;
* fixed direction;
* constant mass;
* zero/constant limiting curves;
* numerical treatment;
* relationship to drag;
* default educational curve;
* explicit real-world omissions.

Remove or qualify outdated statements implying thrust magnitude is constant in the current default model.

Retain constant-thrust behavior as a validated limiting case.

---

# 60. Update `docs/VALIDATION.md`

Document actual Prompt 04 evidence:

* sample validation;
* interpolation;
* exact total impulse;
* delivered impulse;
* constant-thrust regression;
* impulse-momentum validation;
* sample-boundary cases;
* burn-end case;
* active-drag interaction;
* convergence;
* FPS independence;
* reset determinism;
* UI sourcing;
* final test result.

Do not merely describe intended future tests.

---

# 61. Update `docs/ARCHITECTURE.md`

Document the actual propulsion boundary.

Likely ownership:

```text
propulsion.py
    sampled curve
    interpolation
    impulse metrics

physics.py
    thrust vector from current T(t)
    gravity / drag / net force

simulation.py
    fixed outer step
    internal propulsion knot segmentation
    lifecycle / state

rendering.py
    Physics Inspector
    force arrows
    motor timeline

app.py
    controls

docs/learning/
    learner-facing validated tutorial
```

Do not create speculative motor databases or propulsion plugins.

---

# 62. Update `docs/MILESTONES.md`

Mark the sampled-thrust milestone complete only after Prompt 04 actually passes all gates.

Add the Living Rocketry Course as a standing cross-cutting requirement rather than a one-time milestone.

Future milestones should explicitly include:

```text
Learning Course impact review
```

in their completion requirements.

---

# 63. Update `PROJECT_UNDERSTANDING.md`

Reflect that RocketSim is now:

> a scientifically validated, interactive rocketry-learning simulator whose educational course evolves with the implemented model.

Document current propulsion limitations accurately.

---

# 64. Update README

Add a prominent link to:

```text
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
```

Describe it as the guided learning entry point.

Keep developer setup concise.

---

# 65. Research log

Add a concise research-style entry if useful.

A good Prompt 04 question is:

> Does the simulator's velocity change in a zero-gravity, zero-drag constant-mass case agree with independently integrated motor impulse?

or:

> Does internal sample-boundary splitting preserve total thrust impulse when physics timesteps do not align with thrust-curve knots?

Record quantitative evidence, not a Git changelog.

---

# 66. Post-implementation review

After initial implementation and tests, invoke:

* `propulsion_reviewer`;
* `physics_reviewer`;
* `numerical_reviewer`;
* `test_reviewer`;
* `learning_reviewer`.

Also invoke `aerodynamics_reviewer` for a focused regression review because the stepping implementation and force composition operate with drag active.

Wait for all required reports.

---

# 67. Propulsion post-review

Require a direct answer:

> Does Prompt 04 correctly implement the documented piecewise-linear sampled thrust model and impulse semantics?

Inspect:

* instantaneous thrust;
* interpolation;
* curve boundaries;
* impulse;
* average/peak;
* default curve;
* constant-thrust limit;
* exact burn end;
* numerical integration;
* real-vs-synthetic claims.

---

# 68. Physics post-review

Require:

> Does the resulting gravity + time-varying thrust + quadratic-drag model remain physically coherent within the documented constant-mass assumptions?

Inspect:

* signs;
* force sum;
* direction;
* burnout;
* liftoff semantics;
* drag interaction;
* constant mass.

---

# 69. Numerical post-review

Require:

> Does the numerical implementation faithfully handle time-varying thrust and curve boundaries without corrupting the validated drag/event behavior?

Inspect:

* sample-boundary splitting;
* thrust impulse;
* burn-end handling;
* outer fixed timestep;
* accumulator;
* position update;
* drag evaluation;
* convergence;
* deterministic behavior.

---

# 70. Test post-review

Require:

> Could an incorrect sampled-thrust implementation still pass the current tests?

Inspect:

* independent interpolation oracles;
* independent impulse oracles;
* constant-thrust regression;
* impulse-momentum case;
* knot crossing;
* burn end;
* zero-thrust case;
* convergence;
* FPS;
* reset;
* UI sourcing.

---

# 71. Learning post-review

Require:

> Does the Living Rocketry Course accurately teach Prompts 02–04 as the current simulator actually behaves?

Inspect the entire course, not merely the new propulsion chapter.

Check whether Prompt 04 made any older statements obsolete.

---

# 72. Resolve specialist findings

For every BLOCKING finding:

1. investigate independently;
2. correct code/tests/docs/course as appropriate;
3. rerun affected validation;
4. obtain another review from relevant specialist when material.

Address IMPORTANT findings unless clearly outside Prompt 04.

Do not broaden scope to satisfy OPTIONAL suggestions.

Record technically justified deferrals.

---

# 73. Required automated validation

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

Also run focused:

* propulsion unit tests;
* impulse tests;
* constant-thrust regression;
* sample-boundary tests;
* burn-end tests;
* active-drag integration;
* convergence tests;
* FPS independence;
* reset determinism;
* rendering/UI tests.

Do not add lint/type dependencies solely for generic tooling.

---

# 74. Application smoke validation

Run a bounded dummy SDL application smoke test.

Run the real Pygame application where possible.

Inspect:

* motor timeline;
* current thrust;
* cursor movement;
* force arrows;
* Inspector values;
* powered/coast transition;
* delivered impulse;
* total impulse;
* pause/single-step.

Do not claim keyboard interaction if the environment cannot actually perform it.

---

# 75. Educational visual validation

Inspect at least:

### Early ignition

The curve should show increasing thrust and the cursor near the start.

### Near peak thrust

Current thrust should correspond to the curve.

### Declining thrust

The learner should be able to see thrust falling even before burnout.

### Burnout

Current thrust should become zero at the curve's end.

### Coast

Timeline remains visible while thrust is zero.

### Paused single-step

The cursor and current thrust should change exactly with the stepped simulation state.

---

# 76. Final course audit

Before commit, explicitly review:

```text
docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
```

against:

```text
docs/PHYSICS_MODEL.md
docs/VALIDATION.md
actual UI controls
actual Physics Inspector
actual propulsion model
```

Confirm:

* no obsolete constant-thrust-default claims;
* no claim that mass changes;
* no real-motor claim for synthetic data;
* no future feature described as implemented;
* equations agree;
* units agree;
* experiments can actually be performed.

---

# 77. Final repository audit

Before committing:

```bash
git status
git diff
git diff --check
```

Confirm:

* no credentials;
* no environments;
* no caches;
* no generated junk;
* only intended persistent agents;
* no variable mass;
* no propellant depletion;
* no motor database;
* no networking;
* no wind;
* no atmosphere variation;
* no rotation/stability;
* no recovery;
* no Prompt 05 implementation;
* course policy is durable;
* course exists;
* course reflects current simulator;
* documentation matches code;
* old validated physics remains protected.

---

# 78. Implementation commit

After all review/validation gates pass, commit the implementation.

Suggested message:

```text
Implement sampled motor thrust curves and living course
```

The implementation commit should contain:

* propulsion model;
* tests;
* propulsion reviewer;
* learning reviewer;
* `AGENTS.md` policies;
* timeline UI;
* Physics Inspector updates;
* Living Rocketry Course;
* documentation;
* relevant decisions;
* research-log update if appropriate.

Do not include the final Prompt 04 record yet.

---

# 79. Prompt archive

Create the next prompt record, expected approximately:

```text
docs/prompts/prompt_04_propulsion_learning.md
```

Use the actual next unused Prompt ID.

Preserve this complete Prompt 04 verbatim.

Also preserve material follow-up/resume instructions.

Record:

* starting repository state;
* specialist setup;
* Living Course policy;
* course structure;
* propulsion model;
* interpolation contract;
* numerical method;
* default thrust curve;
* pre-review findings;
* reconciliation;
* implementation;
* files changed;
* quantitative impulse evidence;
* convergence;
* UI timeline;
* course review;
* post-review findings;
* fixes;
* deferred findings;
* implementation SHA;
* exact implementation parent diff;
* target remote;
* push status at record creation.

Commit the record separately.

Suggested message:

```text
Record prompt 04 propulsion and learning implementation
```

Do not amend the implementation commit.

---

# 80. Push and final verification

Push without force:

```bash
git push origin main
```

Then verify:

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -n 12
git ls-remote origin refs/heads/main
```

Confirm:

* branch is `main`;
* `main` tracks `origin/main`;
* implementation commit exists;
* Prompt 04 record commit follows it;
* both are pushed;
* local and remote SHAs match;
* working tree is clean.

Do not claim push success unless Git confirms it.

---

# 81. Definition of done — Living Rocketry Course

Prompt 04 is incomplete unless:

* `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md` exists;
* `AGENTS.md` contains the permanent course-maintenance policy;
* future physics milestones are required to review/update the course;
* the parent agent is explicitly told not to wait for a prompt to request the update;
* course scientific truth derives from authoritative docs;
* existing Prompt 02–03 concepts are backfilled;
* the Prompt 04 propulsion lesson exists;
* guided experiments exist;
* model limitations are explicit;
* check-your-understanding material exists;
* `learning_reviewer` reports no unresolved BLOCKING issue.

---

# 82. Definition of done — propulsion

Prompt 04 is incomplete unless:

* sampled thrust curves exist;
* interpolation is validated;
* burn-end semantics are explicit;
* total impulse is independently validated;
* delivered impulse is independently validated;
* peak thrust is correct;
* average thrust is correct;
* sample-boundary behavior is validated;
* constant-thrust equivalence is validated;
* zero-thrust behavior is validated;
* impulse-momentum behavior is validated;
* active drag remains correct;
* mass remains constant;
* no propellant depletion exists.

---

# 83. Definition of done — educational UI

Prompt 04 is incomplete unless:

* current time-varying thrust appears in the Inspector;
* motor metrics are visible;
* the thrust curve is visible;
* current-time cursor is visible;
* timeline data comes from production propulsion data;
* delivered and total impulse are displayed correctly;
* paused single-step updates the timeline correctly;
* UI rendering does not mutate physics;
* application smoke passes.

---

# 84. Definition of done — scientific process

Prompt 04 is incomplete unless:

* all required tests pass;
* focused validation passes;
* no required specialist has unresolved BLOCKING findings;
* documentation is synchronized;
* course is synchronized;
* implementation commit exists;
* Prompt 04 record exists separately;
* both commits are pushed;
* local/remote state agrees;
* final worktree is clean.

---

# 85. Prompt 05 remains undecided

Do not begin Prompt 05.

After Prompt 04, reassess the most educational next single physical effect.

Likely candidates include:

```text
variable mass / propellant depletion
constant wind
altitude-dependent atmosphere
```

Variable mass is a strong candidate because Prompt 04 will isolate the effect of time-varying thrust first, allowing a later learner to see separately how decreasing mass affects acceleration.

But do not implement any of those now.

---

# 86. Completion report

When finished, provide a complete report with separate sections for:

1. starting repository state;
2. Python environment;
3. specialist agents used;
4. `propulsion_reviewer` creation/invocation status;
5. `learning_reviewer` creation/invocation status;
6. pre-review findings;
7. reconciled thrust-curve representation;
8. sample validation rules;
9. interpolation semantics;
10. burn-start/burn-end semantics;
11. numerical impulse treatment;
12. sample-boundary splitting;
13. liftoff treatment for zero initial thrust;
14. default synthetic thrust curve;
15. default curve total impulse;
16. peak thrust;
17. average thrust;
18. delivered impulse behavior;
19. impulse-momentum validation;
20. constant-thrust Prompt 03 regression;
21. zero-thrust regression;
22. active-drag interaction;
23. convergence result;
24. FPS-independence result;
25. deterministic-reset result;
26. Physics Inspector changes;
27. motor timeline implementation;
28. paused single-step timeline behavior;
29. graphical/dummy SDL validation;
30. Living Rocketry Course path;
31. course standing policy;
32. course chapters created;
33. guided experiments added;
34. check-your-understanding material;
35. real-world-vs-model distinctions;
36. learning-review result;
37. post-review findings from every specialist;
38. fixes made because of review;
39. rejected/deferred findings;
40. final pytest count/result;
41. focused test results;
42. decisions created;
43. documentation updated;
44. research-log update;
45. final diff audit;
46. `git diff --check`;
47. implementation commit SHA/message;
48. Prompt 04 record path;
49. Prompt-record commit SHA/message;
50. remote/branch;
51. push result;
52. final local/upstream/remote SHA;
53. final working-tree status;
54. remaining scientific limitations;
55. recommended considerations for Prompt 05.

Do not begin Prompt 05.
~~~~~~~

## First interruption/resume instruction (verbatim)

~~~~~~~text
Please resume and complete Prompt 04 from the exact current repository state.

The previous execution was interrupted only because the Codex/Work usage limit was reached during the pre-implementation specialist-review stage. Do not restart Prompt 04, undo existing valid work, discard the two new specialist definitions, or redo completed work unnecessarily.

First inspect the current Git working tree and determine exactly which Prompt 04 requirements are complete and which remain outstanding. Continue from the first incomplete required step.

Known completed work before interruption includes:

* full Prompt 04 reading and repository audit;
* clean Prompt 03 baseline verification at `c9e1c17`;
* Python 3.12 / `rocketsim` Conda environment verification;
* 119 Prompt 03 tests passing;
* creation and `tomllib` validation of:

  * `.codex/agents/propulsion_reviewer.toml`
  * `.codex/agents/learning_reviewer.toml`
* confirmation that all six specialist definitions are read-only, high-effort, and have no pinned model;
* use of Decision 04’s honest named delegated-agent fallback because the runtime cannot hot-load the new custom agent types;
* completed pre-reviews from:

  * `propulsion_reviewer`
  * `physics_reviewer`
  * `numerical_reviewer`
  * `aerodynamics_reviewer`

The `test_reviewer` and `learning_reviewer` were still running or had not yet returned their completed pre-review reports when usage was exhausted. Obtain and wait for those required reports before central implementation.

The first three scientific reviewers independently converged on the following provisional contract:

* one immutable sampled thrust curve;
* half-open instantaneous thrust semantics;
* piecewise-linear interpolation;
* exact trapezoidal thrust impulse;
* fixed-direction thrust impulse vector;
* internal splitting at every crossed thrust-curve knot;
* gravity and segment-start-velocity drag applied once per internal segment;
* resulting-state force/acceleration telemetry recomputed from the resulting time and velocity.

They also identified a material Prompt 04 issue that must be explicitly reconciled before implementation:

The proposed default synthetic curve starts at `T(0)=0 N`. Under RocketSim’s retained no-pad/no-contact model, the first `0.01 s` interval produces insufficient upward impulse to overcome gravity, causing the numerical trajectory to move below ground. Do not hide this with a clamp, invented support force, or undocumented lifecycle exception.

Before choosing a fix:

1. obtain the completed `test_reviewer` and `learning_reviewer` pre-reviews;
2. reconcile all five primary pre-reviews plus the focused aerodynamics review;
3. independently verify the ignition/liftoff mathematics;
4. choose the smallest scientifically defensible solution consistent with Prompt 04;
5. document the resolution and any adjusted synthetic curve/metrics.

The Prompt 04 wording permits adjustment of the proposed default educational curve if specialist review identifies a compelling reason. If the default curve must be changed to remain launchable without pad/contact physics, update all independently derived default metrics and tests accordingly.

Preserve the educational distinction between:

* instantaneous thrust at an exact time; and
* impulse delivered over a finite interval.

If useful, retain a separate zero-at-ignition educational/validation example under conditions where ground-contact semantics do not invalidate it, rather than falsely implying the current simulator models a launch pad.

Then continue Prompt 04 end-to-end, including:

* reconciled propulsion design;
* Living Rocketry Course standing policy;
* `propulsion_reviewer` and `learning_reviewer` integration into `AGENTS.md`;
* sampled thrust-curve implementation;
* exact interpolation and impulse semantics;
* internal knot-boundary handling;
* burn-end semantics;
* total/delivered impulse;
* peak and average thrust;
* constant-thrust and zero-thrust limiting cases;
* impulse-momentum validation;
* Prompt 03 regression;
* active-drag interaction;
* convergence;
* FPS independence;
* deterministic reset;
* Physics Inspector propulsion updates;
* motor/thrust timeline;
* paused single-step timeline behavior;
* creation and backfilling of:
  `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md`
* permanent Living Rocketry Course policy;
* Decision 06 and Decision 07 using the actual next IDs;
* full post-implementation reviews by all required specialists, including focused aerodynamics review;
* resolution of every BLOCKING finding and applicable IMPORTANT finding;
* full automated and graphical validation;
* final course consistency audit;
* final diff/repository audit;
* implementation commit;
* separate Prompt 04 record with implementation SHA and exact parent diff;
* separate prompt-record commit;
* non-force push to `origin/main`;
* final local/upstream/remote SHA agreement;
* clean working tree verification.

Do not add variable mass, propellant depletion, wind, atmosphere variation, rotation/stability, recovery, motor databases, networking, or Prompt 05 work.

Do not begin Prompt 05.

When complete, provide the full Prompt 04 completion report required by the original Prompt 04.
~~~~~~~

## Second interruption/resume instruction (verbatim)

~~~~~~~text
Please resume and complete Prompt 04 from the exact current repository state.

The previous execution was interrupted solely because the Codex/Work usage limit was reached. Do not restart Prompt 04, undo valid work, discard the current implementation, regenerate already completed work, or repeat completed specialist pre-reviews unnecessarily.

Begin by inspecting the current working tree, Git state, and existing Prompt 04 changes. Determine precisely which Prompt 04 requirements are already complete and which remain outstanding. Continue from the first incomplete required gate.

Known completed work before interruption includes:

- full Prompt 04 reading;
- clean Prompt 03 baseline verification at `c9e1c17`;
- Python 3.12.14 `rocketsim` Conda environment verification;
- original 119 Prompt 03 tests passing before Prompt 04 changes;
- creation and `tomllib` validation of:
  - `.codex/agents/propulsion_reviewer.toml`
  - `.codex/agents/learning_reviewer.toml`
- all required Prompt 04 pre-implementation reviews completed:
  - `propulsion_reviewer`
  - `physics_reviewer`
  - `numerical_reviewer`
  - `test_reviewer`
  - `learning_reviewer`
  - focused `aerodynamics_reviewer`
- Decision 04 fallback used honestly for newly added custom specialists because this runtime could not hot-load the checked-in custom agent types;
- reconciliation of sampled-thrust semantics;
- resolution of the default ignition/liftoff blocker;
- sampled-thrust production implementation;
- propulsion configuration/model integration;
- exact thrust-curve impulse handling;
- curve-knot splitting;
- burn-end handling;
- active-drag interaction;
- current-state force recomputation;
- propulsion unit/integration/validation tests;
- motor timeline / propulsion presentation work;
- Living Rocketry Course work;
- Decision 06 and Decision 07 work;
- synchronization work across scientific/product/validation/milestone documentation;
- focused implementation suite reaching 158 passing tests at the point reported before the documentation phase continued.

The reconciled ignition decision is important and must be preserved unless subsequent specialist review demonstrates a concrete defect:

The originally proposed synthetic curve:

    (0.00, 0)
    (0.05, 28)
    (0.12, 24)
    (0.35, 20)
    (0.70, 16)
    (0.95, 8)
    (1.05, 0)

cannot launch from the default ground state under RocketSim's intentionally retained no-pad/no-contact model. Independent arithmetic showed that during the first 0.01 s its thrust impulse is only 0.028 N*s while gravity contributes 0.0981 N*s downward.

The launchable default was therefore adjusted to begin at 12 N while retaining the remaining curve shape:

    (0.00, 12)
    (0.05, 28)
    (0.12, 24)
    (0.35, 20)
    (0.70, 16)
    (0.95, 8)
    (1.05, 0)

Independent expected metrics are:

    burn duration = 1.05 s
    peak thrust   = 28 N
    total impulse = 17.58 N*s
    average thrust = 16.742857142857... N

This default is synthetic educational data, not a commercial or measured motor.

The original zero-at-ignition 17.28 N*s curve remains useful as an airborne and/or zero-gravity educational/validation case. Do not represent it as a valid default ground launch under the current no-contact model.

This resolution deliberately avoids:
- artificial force clamps;
- look-ahead liftoff hacks;
- hidden pad support;
- launch-rail/contact physics;
- undocumented lifecycle exceptions.

Preserve the educational distinction between instantaneous thrust at a time and impulse delivered over a finite interval.

Before continuing implementation, audit the current diff carefully.

In particular, the interrupted diff showed a modification to:

    .codex/agents/physics_reviewer.toml

with approximately +3/-2 lines.

The Prompt 04 scope did not inherently require changing the existing physics-reviewer definition. Inspect that diff explicitly. If the modification is scientifically/policy necessary, document why. If it is accidental or unnecessary, restore only that unintended change. Do not broadly revert other Prompt 04 work.

Also verify that the two new reviewer TOMLs remain correct, read-only, high-effort, and without pinned model overrides.

Then continue from the first incomplete Prompt 04 requirement.

At minimum, complete all remaining gates:

1. Finish any incomplete documentation/course synchronization.
2. Verify `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md` is complete and internally coherent.
3. Verify the permanent Living Rocketry Course policy is present in `AGENTS.md`.
4. Verify the parent-agent rule explicitly says future applicable milestones must review/update the course without waiting for a prompt to request it.
5. Verify Decision 06 and Decision 07 accurately describe the final implementation rather than planned behavior.
6. Verify `docs/PHYSICS_MODEL.md`, `docs/VALIDATION.md`, `docs/ARCHITECTURE.md`, `docs/MILESTONES.md`, `PROJECT_UNDERSTANDING.md`, README, and the course are synchronized with the actual implementation.
7. Confirm all expected default-thrust metrics use the revised 12 N initial sample and not the obsolete 17.28 N*s default metrics.
8. Retain the original 17.28 N*s zero-at-ignition curve only where explicitly identified as a non-ground-launch educational/validation case.
9. Run focused propulsion validation after all current edits.
10. Run the complete pytest suite.
11. Run compile/import validation.
12. Rerun impulse-momentum validation.
13. Rerun constant-thrust Prompt 03 regression.
14. Rerun zero-thrust regression.
15. Rerun sample-boundary and multi-knot cases.
16. Rerun non-aligned burn-end validation.
17. Rerun active-drag interaction.
18. Rerun timestep-convergence evidence.
19. Rerun FPS-independence validation through the public accumulator.
20. Rerun deterministic-reset validation.
21. Rerun Physics Inspector / motor-timeline sourcing tests.
22. Rerun paused single-step timeline/knot-crossing tests.
23. Run bounded dummy SDL application validation.
24. Perform real graphical inspection where possible without falsely claiming unavailable physical keyboard interaction.
25. Invoke all required Prompt 04 post-implementation specialists:
    - `propulsion_reviewer`
    - `physics_reviewer`
    - `numerical_reviewer`
    - `test_reviewer`
    - `learning_reviewer`
    - focused `aerodynamics_reviewer`
26. Require those reviewers to inspect the actual final implementation, tests, documentation, timeline UI, and Living Rocketry Course.
27. Resolve every valid BLOCKING finding.
28. Address all applicable IMPORTANT findings.
29. Obtain final-resolution re-review where a material correction changes reviewed behavior.
30. Confirm no unresolved completion-blocking scientific, numerical, propulsion, aerodynamic, test, or learning-course finding remains.
31. Perform a final course consistency audit against:
    - `docs/PHYSICS_MODEL.md`
    - `docs/VALIDATION.md`
    - actual simulator controls
    - actual Physics Inspector
    - actual motor timeline
    - actual propulsion model
32. Confirm the course does not:
    - claim variable mass exists;
    - claim the synthetic motor is real measured motor data;
    - describe future features as implemented;
    - retain obsolete constant-thrust-default statements;
    - retain obsolete 17.28 N*s metrics for the revised default;
    - contradict current controls or equations.
33. Run:
    - `conda run -n rocketsim python -m compileall -q src tests`
    - `conda run -n rocketsim python -m pytest`
    - `conda run -n rocketsim python -c "import rocket_sim"`
    - `git diff --check`
34. Inspect the entire final diff for scope contamination.
35. Confirm there is no:
    - variable mass;
    - propellant depletion;
    - specific impulse model;
    - motor database;
    - networking;
    - wind;
    - atmosphere variation;
    - rotation/stability;
    - recovery;
    - Prompt 05 implementation;
    - generated junk;
    - environment files;
    - credentials.
36. Create the Prompt 04 implementation commit only after all required gates pass.
37. Obtain the implementation SHA and exact zero-context diff against its parent.
38. Create the separate Prompt 04 record using the actual next prompt-record filename.
39. Preserve the original Prompt 04 verbatim in that record.
40. Preserve both material interruption/resume instructions as required by the repository workflow.
41. Record:
    - ignition blocker;
    - independent arithmetic;
    - adjusted default curve;
    - revised 17.58 N*s metrics;
    - zero-at-ignition educational case;
    - specialist findings;
    - quantitative validation;
    - course creation/policy;
    - final implementation SHA;
    - exact implementation diff.
42. Commit the Prompt 04 record separately.
43. Push both commits to `origin/main` without force.
44. Verify:
    - local `main`;
    - `origin/main`;
    - remote `refs/heads/main`
    all resolve to the same final prompt-record commit.
45. Verify the final working tree is clean.

Do not begin Prompt 05.

Do not add variable mass, propellant depletion, wind, altitude-dependent atmosphere, rotation, stability, recovery, guidance/control, motor databases, networking, or other future systems.

When complete, provide the entire Prompt 04 completion report required by the original Prompt 04, including:

- final test count;
- default curve;
- total/average/peak thrust metrics;
- zero-at-ignition educational case;
- impulse-momentum evidence;
- knot/burn-end evidence;
- convergence;
- FPS/reset results;
- Physics Inspector and timeline status;
- Living Rocketry Course path and chapter coverage;
- permanent course policy;
- all specialist findings and resolutions;
- Decision 06 and 07;
- implementation commit SHA;
- Prompt 04 record path;
- prompt-record commit SHA;
- push verification;
- final local/upstream/remote SHA;
- final clean Git status.

Do not start Prompt 05.
~~~~~~~

## Final interruption/resume instruction (verbatim)

~~~~~~~text
Please resume and complete Prompt 04 from the exact current repository state.

The previous execution was interrupted solely by the Codex/Work usage limit during the post-implementation review-resolution stage.

Do not restart Prompt 04.
Do not undo valid current work.
Do not regenerate the propulsion implementation, Living Rocketry Course, decisions, UI, or tests.
Do not repeat completed pre-reviews or completed post-reviews unnecessarily.

First inspect:

    git status
    git diff
    git diff --check

and determine exactly which post-review findings have already been resolved and which final gates remain incomplete.

Preserve the current reconciled scientific design.

Known completed work includes:

- full Prompt 04 implementation;
- sampled piecewise-linear thrust curves;
- exact trapezoidal thrust impulse integration;
- splitting at crossed thrust-curve knots;
- constant rocket mass;
- active quadratic drag integration;
- launchable synthetic default curve:

    (0.00, 12)
    (0.05, 28)
    (0.12, 24)
    (0.35, 20)
    (0.70, 16)
    (0.95, 8)
    (1.05, 0)

- default metrics:

    burn duration = 1.05 s
    peak thrust = 28 N
    total impulse = 17.58 N*s
    average thrust = 16.742857142857... N

- separate original zero-at-ignition educational/validation curve with
  17.28 N*s total impulse;
- Physics Inspector propulsion information;
- motor thrust timeline;
- paused single-step timeline behavior;
- `propulsion_reviewer`;
- `learning_reviewer`;
- permanent Living Rocketry Course policy;
- `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md`;
- Decision 06;
- Decision 07;
- synchronized Prompt 04 scientific/product documentation;
- 158 passing tests before the latest review-driven corrections;
- production-rendered visual inspection;
- timeline-layout correction.

All Prompt 04 pre-implementation reviews were already completed.

Post-implementation review status before interruption:

- propulsion_reviewer: completed initial post-review; no blocker;
- physics_reviewer: completed initial post-review; no blocker;
- numerical_reviewer: completed post-review; no blocker;
- aerodynamics_reviewer: completed focused post-review;
- test_reviewer: completed meaningful review and identified event/telemetry evidence issues;
- learning_reviewer: completed meaningful review with no scientific blocker and pedagogical corrections;
- some specialists were being re-invoked for final-resolution confirmation when usage was exhausted.

Do not repeat an already completed review unless a material fix made after that review requires it.

Important review-resolution decisions to preserve:

1. Do not replace the established Prompt 02/03 landing/impact interpolation semantics with a new root solver merely to improve Prompt 04 powered-impact impulse accounting.

2. Decision 03's deterministic linear interpolation of the discrete crossing remains authoritative unless explicitly superseded by a separately approved future decision.

3. Powered-impact partial-curve impulse behavior should be documented and regression-tested consistently with that existing event model rather than silently changing the ground-event algorithm.

4. The nonzero final thrust-curve sample, if supported by the generic curve model, represents a left-limit curve endpoint; instantaneous thrust remains zero at exact and after burn end under the half-open burn interval.

5. Decision/archive links should accurately show how Decision 07 supersedes the constant-thrust propulsion portion of Decision 02 without falsely superseding unrelated Prompt 02 contracts.

6. The Living Rocketry Course improvements already made should be preserved, including:
   - overlay-state guidance;
   - momentum/impulse notation scaffolding;
   - precise burnout language;
   - precise terminal-velocity language;
   - knot-mesh/numerical limitations;
   - READY motor-state explanation.

Audit `.codex/agents/physics_reviewer.toml` carefully.

The prior resume intentionally restored an unnecessary Prompt 04 modification to the existing physics reviewer definition. The current diff still appeared to show approximately `+2/-3` for that file at interruption.

Inspect the exact diff.

If those remaining changes are accidental/unnecessary Prompt 04 residue, restore that file to its Prompt 03 committed state.

If any remaining change is genuinely required, explain why before retaining it.

Do not broadly revert any other Prompt 04 files.

Then finish the remaining Prompt 04 gates:

1. Finish all unresolved post-review corrections.
2. Obtain final-resolution confirmation from any specialist whose reviewed area materially changed after its previous report.
3. Confirm no unresolved BLOCKING finding remains from:
   - propulsion_reviewer
   - physics_reviewer
   - numerical_reviewer
   - test_reviewer
   - learning_reviewer
   - focused aerodynamics_reviewer
4. Address remaining applicable IMPORTANT findings.
5. Rerun focused propulsion tests.
6. Rerun impulse-momentum validation.
7. Rerun interpolation and impulse tests.
8. Rerun single-knot and multi-knot boundary tests.
9. Rerun non-aligned burn-end validation.
10. Rerun constant-thrust Prompt 03 regression.
11. Rerun zero-thrust regression.
12. Rerun the zero-at-ignition airborne/zero-gravity educational case.
13. Rerun active-drag interaction tests.
14. Rerun powered-impact regression consistent with Decision 03 semantics.
15. Rerun timestep convergence.
16. Rerun FPS independence through the public accumulator.
17. Rerun deterministic reset.
18. Rerun Physics Inspector and timeline sourcing tests.
19. Rerun paused single-step / knot-crossing tests.
20. Rerun course-documented headless activities where appropriate.
21. Run:

    conda run -n rocketsim python -m compileall -q src tests
    conda run -n rocketsim python -m pytest
    conda run -n rocketsim python -c "import rocket_sim"
    git diff --check

22. Report the new final test count rather than assuming it remains 158 after review-driven tests were added.
23. Run bounded dummy SDL validation.
24. Perform any final production-frame inspection needed after rendering changes.
25. Perform the complete Living Rocketry Course consistency audit against:
    - docs/PHYSICS_MODEL.md
    - docs/VALIDATION.md
    - actual controls
    - Physics Inspector
    - motor timeline
    - propulsion implementation
26. Confirm all revised-default references use:
    - 12 N initial thrust
    - 17.58 N*s total impulse
    - 16.742857... N average thrust
27. Confirm 17.28 N*s appears only where clearly identified as the original zero-at-ignition educational/validation curve.
28. Confirm the course does not claim:
    - variable mass;
    - propellant depletion;
    - specific impulse;
    - real measured motor data;
    - future physics as implemented.
29. Confirm Decision 06 and Decision 07 describe actual final behavior.
30. Perform the complete final repository diff audit.
31. Confirm no scope contamination:
    - no variable mass;
    - no propellant depletion;
    - no motor database/networking;
    - no wind;
    - no altitude-dependent atmosphere;
    - no rotation/stability;
    - no recovery;
    - no Prompt 05 work;
    - no credentials/environments/generated junk.
32. Run final `git diff --check`.
33. Create the Prompt 04 implementation commit only after every required gate passes.
34. Obtain the implementation SHA and exact zero-context parent diff.
35. Create the separate Prompt 04 prompt record using the actual repository naming convention.
36. Preserve the original Prompt 04 verbatim.
37. Preserve all material interruption/resume instructions required by repository policy.
38. Record:
    - ignition blocker;
    - initial impulse arithmetic;
    - adjusted launchable default curve;
    - 17.58 N*s metrics;
    - original 17.28 N*s educational curve;
    - exact curve/impulse semantics;
    - knot handling;
    - powered-impact limitation;
    - specialist findings/resolutions;
    - course policy/course contents;
    - quantitative validation;
    - implementation SHA;
    - exact implementation diff.
39. Commit the Prompt 04 record separately.
40. Push both commits to `origin/main` without force.
41. Verify:

    git status
    git branch -vv
    git remote -v
    git log --oneline --decorate -n 12
    git ls-remote origin refs/heads/main

42. Confirm local HEAD, `origin/main`, and remote `refs/heads/main` all agree.
43. Confirm the final working tree is clean.

Do not begin Prompt 05.

When finished, provide the complete Prompt 04 completion report required by the original Prompt 04, including the final test count, final specialist statuses, quantitative propulsion validation, timeline/UI validation, Living Rocketry Course status, Decision 06/07, implementation commit, prompt-record commit, push verification, and final Git state.
~~~~~~~

## Exact implementation commit diff against parent

The following is the exact zero-context, binary-capable diff produced by:

```bash
git show --no-ext-diff --binary --unified=0 --format= 9cd39497240ad52ffa42a6e55e30f8fd82bc75b0
```

~~~~~~~diff
diff --git a/.codex/agents/learning_reviewer.toml b/.codex/agents/learning_reviewer.toml
new file mode 100644
index 0000000..08c1aef
--- /dev/null
+++ b/.codex/agents/learning_reviewer.toml
@@ -0,0 +1,53 @@
+name = "learning_reviewer"
+description = "Independently reviews RocketSim's living rocketry course for scientific consistency, pedagogical clarity, implemented-only claims, guided experiments, and synchronization with the simulator."
+
+sandbox_mode = "read-only"
+model_reasoning_effort = "high"
+
+developer_instructions = """
+You are RocketSim's independent learning-course reviewer.
+
+You are a reviewer, not an implementation agent.
+
+Do not modify repository files.
+
+RocketSim is both a scientifically inspectable simulator and an interactive
+environment for learning rocketry.
+
+Your primary question is:
+
+Does the Living Rocketry Course accurately and clearly teach the validated
+physics that the current simulator actually implements?
+
+Review:
+- consistency with docs/PHYSICS_MODEL.md
+- consistency with docs/VALIDATION.md
+- consistency with actual simulator controls and UI
+- SI units
+- coordinate conventions
+- equations
+- force directions
+- assumptions and limitations
+- distinction between real-world physics and RocketSim approximation
+- whether future features are incorrectly described as implemented
+- guided simulator activities
+- prediction / observation / explanation structure
+- check-your-understanding questions
+- whether an existing lesson became outdated after a new milestone
+- whether the tutorial explains why the model is simplified
+- whether activities are reproducible with the current simulator
+
+The course should teach concepts progressively and should not merely copy
+developer documentation.
+
+For each important issue report:
+
+SCIENTIFIC ISSUE
+PEDAGOGICAL ISSUE
+SIMULATOR / COURSE MISMATCH
+RECOMMENDED CORRECTION
+
+Classify completion-critical findings as BLOCKING.
+
+Do not modify files.
+"""
diff --git a/.codex/agents/propulsion_reviewer.toml b/.codex/agents/propulsion_reviewer.toml
new file mode 100644
index 0000000..03aea84
--- /dev/null
+++ b/.codex/agents/propulsion_reviewer.toml
@@ -0,0 +1,67 @@
+name = "propulsion_reviewer"
+description = "Independently reviews RocketSim thrust-curve semantics, interpolation, impulse, burn timing, motor metrics, propulsion assumptions, and propulsion validation."
+
+sandbox_mode = "read-only"
+model_reasoning_effort = "high"
+
+developer_instructions = """
+You are RocketSim's independent propulsion reviewer.
+
+You are a reviewer, not an implementation agent.
+
+Do not modify repository files.
+
+Your primary question is:
+
+Does the implementation correctly represent the documented sampled
+time-varying thrust model?
+
+Review:
+- thrust as a function of time
+- sampled thrust data
+- piecewise-linear interpolation
+- sample-boundary behavior
+- ignition-time semantics
+- burn-end semantics
+- thrust before, at, and after burn
+- total impulse
+- delivered impulse
+- average thrust
+- peak thrust
+- thrust-vector magnitude and fixed direction
+- units and dimensional consistency
+- constant-thrust limiting behavior
+- zero-thrust limiting behavior
+- numerical integration of time-varying thrust
+- interaction with drag and gravity
+- educational motor metrics
+- claims about real motors versus synthetic educational data
+
+For Prompt 04, rocket mass remains constant.
+
+Do not introduce:
+- propellant depletion
+- variable mass
+- specific impulse
+- exhaust velocity
+- chamber pressure
+- nozzle design
+- motor chemistry
+- thrust-vector control
+
+Derive expected values independently rather than copying production helpers.
+
+Classify meaningful findings as:
+
+BLOCKING
+IMPORTANT
+OPTIONAL
+
+For every meaningful finding:
+- explain the propulsion issue;
+- reference exact files/functions/tests/equations;
+- state expected behavior;
+- recommend the smallest scientifically defensible correction.
+
+Do not modify files.
+"""
diff --git a/AGENTS.md b/AGENTS.md
index 29d330f..5118de9 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -43,0 +44,8 @@ Invoke for changes involving drag, aerodynamic force, air-relative velocity, ref
+### `propulsion_reviewer`
+
+Invoke for changes involving thrust curves, motor burn timing, thrust interpolation, impulse, average or peak thrust, propulsion assumptions, or later motor models.
+
+### `learning_reviewer`
+
+Invoke before completing any milestone that changes physics, propulsion, Physics Inspector content, educational visualization, learner controls, simulator experiments, or Living Rocketry Course content.
+
@@ -63,0 +72,27 @@ Keep detailed reviewer behavior in `.codex/agents/*.toml`. Keep scientific truth
+## Living Rocketry Course Policy
+
+RocketSim is both a scientifically inspectable simulator and an educational environment for learning rocketry. Maintain `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md` as the living tutorial-style course for the validated simulator.
+
+Any approved milestone that adds or materially changes a physical model, force, equation, propulsion model, numerical interpretation important to understanding the physics, physical event or phase, Physics Inspector information, educational visualization, simulator experiment, or user-facing control relevant to learning must review and, where applicable, update the Living Rocketry Course before the milestone is complete.
+
+The parent agent must not wait for a future prompt to explicitly request a course update.
+
+The course must:
+
+- teach only behavior that is currently implemented and validated;
+- clearly distinguish real-world physics from RocketSim's current approximation;
+- use the equations, units, signs, and coordinate conventions in `docs/PHYSICS_MODEL.md`;
+- remain consistent with the methodology and evidence in `docs/VALIDATION.md`;
+- never present future functionality as implemented;
+- connect concepts to hands-on simulator observations and reproducible experiments;
+- state assumptions and model limitations;
+- use prediction, observation, and explanation activities where appropriate;
+- include check-your-understanding questions; and
+- revise older lessons when a later milestone refines an earlier simplification.
+
+Updating the course may require revising an earlier chapter, not merely appending a new chapter. For example, variable mass would require revisiting powered flight and motor lessons; altitude-varying atmosphere would require revisiting drag; wind would require revisiting air-relative velocity; and rotation or stability would require revisiting thrust direction and point-mass assumptions.
+
+Scientific truth remains in `docs/PHYSICS_MODEL.md`. Validation methodology and evidence remain in `docs/VALIDATION.md`. The Living Rocketry Course is their pedagogical explanation, not an independent source of physics truth.
+
+A physics or educational milestone is not complete until applicable Living Rocketry Course material has been reviewed for consistency. The parent agent remains the sole implementer and integrator; `learning_reviewer` and all other specialists remain read-only.
+
diff --git a/README.md b/README.md
index 57997c7..7fe27f3 100644
--- a/README.md
+++ b/README.md
@@ -3 +3,3 @@
-RocketSim is a scientifically inspectable 2D model-rocket flight simulator built with Python and Pygame. Its current milestone models a constant-mass point rocket under gravity, finite-duration constant thrust, and constant-property quadratic aerodynamic drag in still air. A fixed physics timestep remains independent of display FPS.
+RocketSim is a scientifically inspectable 2D model-rocket flight simulator and interactive rocketry-learning laboratory built with Python and Pygame. Its current milestone models a constant-mass point rocket under gravity, a sampled time-varying thrust curve, and constant-property quadratic aerodynamic drag in still air. A fixed outer physics timestep remains independent of display FPS.
+
+Start with the [Living Rocketry Course](docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md) to learn the implemented physics through prediction, observation, and hands-on simulator experiments.
@@ -7 +9 @@ RocketSim is a scientifically inspectable 2D model-rocket flight simulator built
-Milestone 2 is implemented. The runnable application includes a Physics Inspector and force-vector overlay while a Pygame-independent physics core remains the sole owner of force calculations, integration, event transitions, and history.
+Milestone 3 is implemented. The runnable application includes a Physics Inspector, force-vector overlay, and motor thrust timeline while a Pygame-independent physics core remains the sole owner of force calculations, integration, event transitions, and history.
@@ -13 +15,3 @@ Implemented physics:
-- constant thrust at a fixed world angle for `0 <= t < burn_time`
+- immutable sampled thrust with piecewise-linear `T(t)` at a fixed world angle
+- exact total/delivered motor impulse for the represented curve
+- burn duration derived from the final sample and a half-open burn endpoint
@@ -17 +21 @@ Implemented physics:
-- exact substep split when a fixed step crosses burnout
+- exact internal split at every crossed thrust knot and burnout
@@ -20 +24,3 @@ Implemented physics:
-The aerodynamic defaults are educational constants, not calibration of a real vehicle: `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`. Variable mass, sampled thrust curves, wind, atmosphere variation, lift, recovery, rotation, stability, guidance, and control are not implemented.
+The propulsion default is self-authored synthetic educational data, not measured or certified motor data. It has `1.05 s` duration, `17.58 N*s` total impulse, `28 N` peak thrust, and `16.742857... N` average thrust. The aerodynamic defaults are educational constants, not calibration of a real vehicle: `rho = 1.225 kg/m^3`, `Cd = 0.75`, and `A = 0.01 m^2`.
+
+Variable mass, propellant depletion, motor-data import, launch-pad/rail contact, wind, atmosphere variation, lift, recovery, rotation, stability, guidance, and control are not implemented.
@@ -49 +55,3 @@ Controls:
-The inspector shows phase, burnout status, state, acceleration, mass, all force vectors and magnitudes, the aerodynamic constants, and the implemented equations. Thrust, gravity, drag, and net-force arrows use the same rendering-only scale and are sourced from the force breakdown used by the simulator. The default vertical configuration uses a `1 kg` rocket, `20 N` thrust, a `1 s` burn, and `9.81 m/s^2` gravity, so thrust exceeds weight during launch.
+The inspector shows flight and motor phase, burnout status, state, acceleration, constant mass, current/peak/average thrust, burn-time progress, delivered/total impulse, all force vectors and magnitudes, aerodynamic constants, and implemented equations. The timeline plots the exact production samples and current motor-time cursor; after burnout its endpoint-clamped cursor is labeled as such. Thrust, gravity, drag, and net-force arrows use the same rendering-only scale and are sourced from the force breakdown used by the simulator.
+
+The default vertical configuration uses a `1 kg` rocket and begins at `12 N`, above its `9.81 N` weight. The original zero-at-ignition educational curve is tested only away from the ground boundary because RocketSim does not model a launch-pad support force.
@@ -56,0 +65 @@ tests/                 headless physics, numerical, lifecycle, and rendering tes
+docs/learning/         learner-facing Living Rocketry Course
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 4170e9f..a2c9128 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -14 +14 @@ app.py -> Simulation.advance_elapsed()
-fixed-step accumulator -> simulation.py lifecycle/events
+fixed-step accumulator -> simulation.py lifecycle/events + knot segmentation
@@ -17 +17 @@ fixed-step accumulator -> simulation.py lifecycle/events
-physics.py force breakdown + semi-implicit Euler
+propulsion.py curve geometry -> physics.py force/impulse update
@@ -33,0 +34 @@ rendering.py world transform + drawing + telemetry
+- one authoritative immutable `ThrustCurve`
@@ -35,0 +37,11 @@ rendering.py world transform + drawing + telemetry
+### `propulsion.py`
+
+- immutable `ThrustSample` and defensively tuple-owned `ThrustCurve`
+- sample validation and half-open piecewise-linear interpolation
+- exact total, delivered, and interval impulse from curve geometry
+- burn duration, average thrust, and peak thrust metrics
+- constant-thrust and zero-thrust limiting constructors
+- bundled synthetic educational default curve
+
+It contains no Pygame, motor database, file loader, network access, variable mass, or mutable motor state.
+
@@ -39 +51,2 @@ rendering.py world transform + drawing + telemetry
-- half-open burn predicate
+- instantaneous thrust from the production curve and fixed world direction
+- exact thrust-impulse vector for an interval
@@ -42 +55 @@ rendering.py world transform + drawing + telemetry
-- one force-frozen semi-implicit Euler segment
+- exact-thrust-impulse/start-state-other-force semi-implicit segment update
@@ -52,2 +65,3 @@ It does not own wall time, phases, events, or drawing.
-- exact burnout split with drag reevaluation
-- deterministic ground-crossing handling
+- exact internal splitting at every crossed thrust knot and burn end
+- exact curve thrust impulse plus start-velocity drag on each internal segment
+- deterministic interpolation of the first discrete ground crossing
@@ -63,0 +78 @@ Configuration is the source of constant mass. Every recorded state repeats that
+- production-curve motor timeline, samples, cursor, burnout marker, and metrics
@@ -75 +90,3 @@ Configuration is the source of constant mass. Every recorded state repeats that
-`physics.force_breakdown_n(config, time, velocity)` is the single production source for thrust, gravity, drag, and net force. The simulation uses its net vector for acceleration and exposes the current breakdown for presentation. The renderer receives those vectors and may only scale, label, color, or hide them; it does not import the drag helper or reproduce the aerodynamic equation.
+`physics.force_breakdown_n(config, time, velocity)` is the single production source for instantaneous thrust, gravity, drag, and net force. The simulation exposes that breakdown for presentation. Integration separately obtains exact scalar curve impulse through `propulsion.ThrustCurve` and converts it once to a fixed-direction vector; it combines that impulse with gravity and start-velocity drag without double-counting instantaneous thrust.
+
+The renderer receives the configured production `ThrustCurve` for sample positions and calls its public instantaneous-thrust and impulse-backed simulator values. It may map time/thrust to pixels, clamp a clearly labeled motor cursor at burnout, and format values. It does not construct a second curve, interpolate thrust, integrate trapezoids, or mutate motor/simulation state.
@@ -87 +104,3 @@ No absolute comparison tolerance creates simulation time. Burnout is handled by
-The flight phases are ready, powered, coast, and landed. Pause is an application lifecycle state layered over the physical powered/coast phase. State acceleration describes the instantaneous force model at the state's resulting time and velocity, so a state exactly at burnout is coast even if the preceding interval was powered. A step split at burnout calls the force path independently for the powered and coast segments, so the latter uses updated burnout velocity for drag.
+The flight phases are ready, powered, coast, and landed. Pause is an application lifecycle state layered over the physical powered/coast phase. Powered is the half-open configured motor interval and does not imply that instantaneous thrust must be positive at every time. State acceleration describes the instantaneous force model at the state's resulting time and velocity; it can differ from the average acceleration that produced the segment's velocity change. A state exactly at burnout is coast even if the preceding interval was powered.
+
+Each fixed outer step is partitioned at every strictly crossed curve knot. Every internal segment integrates the curve impulse exactly, reevaluates drag from its own start velocity, updates velocity, then updates position. Internal boundaries may add trajectory samples, but the wall-time accumulator and `physics_step_count` still consume one configured outer step. Curve knots are consequently part of the numerical mesh when drag is active.
@@ -90,0 +110,4 @@ Burnout and landing are handled inside the simulation boundary. A post-liftoff t
+## Learning documentation boundary
+
+`docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md` is the learner-facing tutorial and interactive laboratory guide. It derives equations from `docs/PHYSICS_MODEL.md`, validation claims from `docs/VALIDATION.md`, and controls from the implemented application. It is reviewed retroactively when physics or educational behavior changes; it is not an independent source of scientific truth.
+
@@ -93 +116 @@ Burnout and landing are handled inside the simulation boundary. A post-liftoff t
-Prompt 03 deliberately adds no atmosphere or aerodynamic plugin interface: three constant scalars and one vector equation are sufficient. It does not introduce motor interfaces, wind, lift, data loaders, experiment frameworks, plots, plugins, databases, ECS, networking, or abstractions for unimplemented milestones. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
+Prompt 04 adds the smallest active propulsion boundary: one immutable sampled curve and no general motor-data ecosystem. It does not introduce variable mass, propellant depletion, motor-file import, motor selection, wind, lift, atmosphere variation, experiment frameworks, plugins, databases, ECS, or networking. Later effects should be added one validated physical model at a time without changing the current ownership boundary silently.
diff --git a/docs/MILESTONES.md b/docs/MILESTONES.md
index 9e56157..2c3ca44 100644
--- a/docs/MILESTONES.md
+++ b/docs/MILESTONES.md
@@ -76,0 +77,38 @@ Validation:
+## Milestone 3 — Sampled motor thrust curves and Living Rocketry Course
+
+Status: complete in Prompt 04.
+
+Physics:
+
+- immutable sampled thrust data and piecewise-linear interpolation
+- burn duration derived from the final curve sample
+- exact total, delivered, and interval motor impulse
+- fixed world thrust direction and constant rocket mass
+- exact thrust-impulse velocity contribution on every knot-bounded segment
+- gravity plus segment-start-velocity quadratic drag retained
+- constant-thrust and zero-thrust limiting curves
+
+Features:
+
+- current, peak, and average thrust plus delivered/total impulse in the Physics Inspector
+- production-data motor timeline with samples, cursor, peak, and burnout marker
+- paused single-step updates across thrust knots while remaining paused
+- permanent Living Rocketry Course and retroactive update policy
+- persistent propulsion and learning reviewers
+
+Validation:
+
+- independent curve validation, interpolation, and trapezoidal metrics
+- one/multiple-knot and nonaligned-burn-end literal oracles
+- zero-gravity/zero-drag impulse–momentum agreement
+- Prompt 03 constant-thrust, zero-thrust, drag, lifecycle, timing, and rendering regressions
+- active-drag convergence against an independent RK4 reference
+- sampled-thrust FPS independence and deterministic reset
+- Inspector/timeline production sourcing, non-mutation, and SDL smoke evidence
+
+The default is a synthetic educational curve, not measured motor data. Variable mass and propellant depletion remain unimplemented.
+
+## Standing cross-cutting requirement — Learning Course impact review
+
+Every future approved milestone must identify whether it changes physics, equations, numerical interpretation, phases/events, Inspector information, educational visualization, controls, or experiments. Applicable chapters of `docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md` must be revised and the complete course reviewed before that milestone is complete. This requirement may revise earlier chapters rather than merely append a new one.
+
@@ -82 +120 @@ The following remain unimplemented and require separate approval and validation:
-2. sampled real-motor thrust curves and total impulse
+2. validated real-motor data ingestion
@@ -88,0 +127,2 @@ The following remain unimplemented and require separate approval and validation:
+Each candidate milestone includes a Living Course impact review as a completion gate.
+
diff --git a/docs/PHYSICS_MODEL.md b/docs/PHYSICS_MODEL.md
index 2a7778c..9e0aad7 100644
--- a/docs/PHYSICS_MODEL.md
+++ b/docs/PHYSICS_MODEL.md
@@ -3 +3 @@
-## Implemented Milestone 2 model
+## Implemented Milestone 3 model
@@ -21 +21 @@ World +x is horizontal/right, world +y is upward, and the ground is `y = 0`. Scr
-Each recorded state contains simulation time, position, velocity, instantaneous acceleration, constant mass, flight phase, and whether liftoff has occurred. Configuration contains mass, thrust magnitude, burn duration, fixed world launch angle, gravity magnitude, constant air density, constant drag coefficient, constant reference area, fixed physics timestep, and initial position and velocity.
+Each recorded state contains simulation time, position, velocity, instantaneous acceleration, constant mass, flight phase, and whether liftoff has occurred. Configuration contains mass, one immutable sampled thrust curve, fixed world launch angle, gravity magnitude, constant air density, constant drag coefficient, constant reference area, fixed outer physics timestep, and initial position and velocity.
@@ -23 +23 @@ Each recorded state contains simulation time, position, velocity, instantaneous
-All scalar and vector inputs must be finite. Mass and timestep must be positive. Thrust, burn duration, gravity magnitude, air density, drag coefficient, and reference area may be zero but not negative. Initial altitude may not be below ground.
+All scalar and vector inputs must be finite. Mass and timestep must be positive. Gravity magnitude, air density, drag coefficient, reference area, sample times, and sample thrust values may be zero but not negative. Initial altitude may not be below ground. A normal thrust curve has at least two samples, begins at exactly `t=0`, and has strictly increasing times. The zero-duration limiting curve is the single sample `(0 s, 0 N)`.
@@ -53 +53 @@ These are numerically equal in this milestone but are not interchangeable physic
-For constant mass `m > 0`, gravity magnitude `g >= 0`, thrust magnitude `T >= 0`, fixed angle `theta`, burnout time `t_b >= 0`, air density `rho >= 0`, drag coefficient `Cd >= 0`, reference area `A >= 0`, and air-relative velocity vector `v_air`:
+For constant mass `m > 0`, gravity magnitude `g >= 0`, time-varying thrust magnitude `T(t) >= 0`, fixed angle `theta`, curve-defined burnout time `t_b >= 0`, air density `rho >= 0`, drag coefficient `Cd >= 0`, reference area `A >= 0`, and air-relative velocity vector `v_air`:
@@ -59 +59 @@ F_g = (0, -m g)
-Thrust uses the exact half-open time interval:
+The fixed world thrust direction is:
@@ -62,2 +62,2 @@ Thrust uses the exact half-open time interval:
-F_T(t) = T(cos(theta), sin(theta))  when 0 <= t < t_b
-F_T(t) = (0, 0)                    otherwise
+u_T = (cos(theta), sin(theta))
+F_T(t) = T(t) u_T
@@ -65,0 +66,18 @@ F_T(t) = (0, 0)                    otherwise
+For adjacent stored samples `(t_i,T_i)` and `(t_(i+1),T_(i+1))`, instantaneous thrust is piecewise linear:
+
+```text
+T(t) = T_i
+       + (T_(i+1) - T_i)
+         (t - t_i) / (t_(i+1) - t_i)
+```
+
+The burn interval remains exactly half-open:
+
+```text
+T(t) = 0  for t < 0
+T(t_i) = T_i  at an interior knot
+T(t) = 0  for t >= t_b
+```
+
+The final stored thrust is the left-limit endpoint of the last linear interval even if it is nonzero; it contributes to the final trapezoidal impulse although instantaneous thrust at exact burn end is zero.
+
@@ -102 +120,34 @@ a = F_net / m
-Production code exposes these named vectors in one immutable `ForceBreakdown`. Integration and presentation consume the same calculation. Mass remains constant at ignition, burnout, coast, descent, and landing.
+Production code exposes these named instantaneous vectors in one immutable `ForceBreakdown` for state telemetry and presentation. Integration uses the same gravity and drag helpers but replaces instantaneous thrust with the exact curve impulse over each internal segment, so thrust is not counted twice. Mass remains constant at ignition, burnout, coast, descent, and landing.
+
+## Motor impulse and metrics
+
+Total motor impulse is the exact area under the stored piecewise-linear curve:
+
+```text
+I_total = integral T(t) dt
+        = sum[0.5 (T_i + T_(i+1)) (t_(i+1) - t_i)]
+```
+
+Impulse has units `N*s = kg*m/s`. Delivered impulse clamps the query time to the represented burn:
+
+```text
+I_delivered(t) = integral from 0 to clamp(t, 0, t_b) of T(tau) d tau
+```
+
+It is zero before ignition, monotonic because thrust is non-negative, and equals total impulse at and after burn end. Average and peak thrust are:
+
+```text
+T_average = I_total / t_b  for t_b > 0
+T_average = 0              for the zero-duration curve
+T_peak,stored = max stored sample thrust
+```
+
+Piecewise-linear interpolation cannot exceed its endpoint samples, so this stored peak is the exact supremum of the represented polyline. If a unique nonzero peak occurs only at the final stored endpoint, it is a left-limit value rather than an attained value of the public half-open instantaneous function, because `T(t_b) = 0`. It is not a claim that sparse samples capture the true peak of a measured motor.
+
+For constant mass with gravity and drag disabled, thrust impulse gives:
+
+```text
+delta_v = (I_total / m) u_T
+```
+
+With gravity and drag active, the general momentum balance also includes their impulses. Equal motor impulse alone need not produce the same trajectory.
@@ -106 +157 @@ Production code exposes these named vectors in one immutable `ForceBreakdown`. I
-The default fixed physics timestep remains `dt = 0.01 s`. For each numerical segment, all forces are evaluated from the segment's starting time and velocity. Semi-implicit Euler then updates velocity before position:
+The default fixed outer physics timestep remains `dt = 0.01 s`. Every outer step is split internally at each strictly crossed thrust-curve knot, including a non-aligned burn end. For one internal segment `[t_n,t_(n+1)]` of duration `h`, RocketSim integrates the represented linear thrust exactly while retaining the established explicit drag and semi-implicit position rules:
@@ -109,4 +160,10 @@ The default fixed physics timestep remains `dt = 0.01 s`. For each numerical seg
-F_n = F(t_n, v_n)
-a_n = F_n / m
-v_(n+1) = v_n + a_n dt
-p_(n+1) = p_n + v_(n+1) dt
+J_T = integral from t_n to t_(n+1) of T(t) dt
+    = 0.5 (T_left + T_right) h
+
+F_other_start = F_g + F_drag(v_n)
+
+v_(n+1) = v_n
+            + (J_T / m) u_T
+            + (F_other_start / m) h
+
+p_(n+1) = p_n + v_(n+1) h
@@ -115 +172,3 @@ p_(n+1) = p_n + v_(n+1) dt
-Drag depends on velocity, so acceleration is not constant over the true continuous interval. The method freezes it only for one numerical segment. Prompt 02's constant-acceleration identity:
+`T_left` and `T_right` above are the stored ordinates that bound the represented linear interval. On the final interval, a nonzero `T_right` is the burn-end left limit used by the trapezoid even though the public instantaneous value at exact burnout is zero.
+
+The motor impulse contribution to velocity is exact for every completed internal segment of the stored polyline, and gravity's velocity impulse is exact because gravity is constant. Position is not exact, and drag remains frozen from segment-start velocity. Prompt 02's constant-acceleration identity:
@@ -123 +182,3 @@ continues to apply to the zero-drag constant-acceleration limit, but not general
-If a configured step begins before burnout and ends after it, the simulator performs a powered substep ending exactly at `t_b`, followed by a coast substep for the remainder. The coast substep reevaluates drag from the updated burnout velocity. A state at exact burnout reports zero thrust and force/acceleration evaluated from its burnout velocity.
+If a configured outer step crosses one or more curve knots, every boundary produces a completed internal segment and drag is reevaluated from the updated boundary velocity. A state at exact burnout reports zero thrust and force/acceleration evaluated from its burnout velocity. The outer wall-time accumulator and physics-step count still advance once per configured outer timestep.
+
+Because curve knots are numerical boundaries, adding a redundant collinear sample can introduce an extra drag/position update even though it leaves `T(t)` and motor impulse unchanged. The immutable sample set is therefore part of the numerical configuration. Convergence comparisons keep the same knot set.
@@ -158 +219,5 @@ At `v_y = -v_terminal`, upward drag balances downward weight and net vertical ac
-Ground admission, liftoff, and landing retain Prompt 02 semantics. A ground start must have non-negative initial vertical velocity and a positive first drag-inclusive numerical endpoint. After liftoff, the first descending numerical segment that crosses `y = 0` is linearly interpolated in time, horizontal position, and velocity; altitude is set to exactly zero and the state becomes terminal. This is deterministic interpolation of the discrete numerical path, not an exact impact root.
+Ground admission, liftoff, and landing retain Prompt 02 semantics. A ground start must have non-negative initial vertical velocity and a positive first propulsion-aware internal numerical endpoint. That endpoint uses exact curve impulse plus gravity and start-velocity drag; it does not sample only `T(0)`. RocketSim still has no launch-pad, rail, normal-force, or hold-down model.
+
+The original proposed educational curve began at zero thrust and would move below ground in the first free-flight timestep. It is therefore retained only as an airborne or zero-gravity validation example, not as the ground-launch default. The actual default begins at `12 N`, above the default rocket's `9.81 N` weight. This is a model-scope correction, not a hidden ground clamp.
+
+After liftoff, the first descending numerical segment that crosses `y = 0` is linearly interpolated in time, horizontal position, and velocity; altitude is set to exactly zero and the state becomes terminal. This is deterministic interpolation of the discrete numerical path, not an exact impact root. If impact occurs during time-varying thrust, the interpolated impact velocity is not claimed to equal an exact partial-segment impulse solution. Current forces and delivered impulse are nevertheless recomputed from the reported impact time and velocity.
@@ -166,2 +231,11 @@ mass              1.0 kg
-thrust            20.0 N
-burn duration     1.0 s
+sampled thrust    (0.00 s, 12 N)
+                  (0.05 s, 28 N)
+                  (0.12 s, 24 N)
+                  (0.35 s, 20 N)
+                  (0.70 s, 16 N)
+                  (0.95 s,  8 N)
+                  (1.05 s,  0 N)
+burn duration     1.05 s
+total impulse     17.58 N*s
+peak thrust       28.0 N
+average thrust    16.742857... N
@@ -176 +250 @@ physics timestep  0.01 s
-For this educational approximation, the vertical terminal speed under gravity alone is about `46.21 m/s`. The default flight remains capable of liftoff.
+The thrust curve is self-authored synthetic educational data, not measurement or certification of a commercial motor. For this educational approximation, the vertical terminal speed under gravity alone is about `46.21 m/s`. The default flight remains capable of liftoff without a pad-support rule.
@@ -180 +254 @@ For this educational approximation, the vertical terminal speed under gravity al
-The model has no wind, altitude-varying density, pressure or temperature, lift, orientation-dependent area, variable `Cd`, Mach/Reynolds/compressibility effects, propellant depletion, variable mass, sampled thrust curve, attitude change, rotation, aerodynamic stability, recovery device, bounce, structural dynamics, Earth curvature, or Coriolis effect. Its single direction-independent effective area makes it an isotropic point-mass drag approximation.
+The model has no wind, altitude-varying density, pressure or temperature, lift, orientation-dependent area, variable `Cd`, Mach/Reynolds/compressibility effects, propellant depletion, variable mass, measured motor-data import, pad or launch-rail contact, attitude change, rotation, aerodynamic stability, recovery device, bounce, structural dynamics, Earth curvature, or Coriolis effect. Its single direction-independent effective area makes it an isotropic point-mass drag approximation.
diff --git a/docs/RESEARCH_LOG.md b/docs/RESEARCH_LOG.md
index 145285f..8f67cba 100644
--- a/docs/RESEARCH_LOG.md
+++ b/docs/RESEARCH_LOG.md
@@ -156,0 +157,55 @@ The measured ratios support first-order convergence for this stable nonlinear ca
+
+---
+
+## 2026-08-29 — Sampled motor impulse and knot-boundary integration
+
+### Question
+
+Does RocketSim's velocity change agree with independently integrated motor impulse when thrust varies piecewise linearly, and does knot segmentation retain first-order trajectory convergence when quadratic drag is active?
+
+### Hypothesis
+
+Exact trapezoidal thrust impulse should make the propulsion-only final velocity independent of the fixed timestep. With drag active, trajectory error should remain approximately first order because drag is evaluated from each internal segment's starting velocity and position uses the updated endpoint velocity.
+
+### Model / assumptions
+
+- Constant rocket mass.
+- Fixed world thrust direction.
+- Immutable piecewise-linear sampled thrust.
+- Exact thrust impulse on completed knot-bounded segments.
+- Constant gravity.
+- Still-air quadratic drag with constant density, `Cd`, and area.
+- No launch support, propellant depletion, variable mass, or real motor data.
+
+### Method and results
+
+A zero-gravity, zero-drag curve with independently summed total impulse `10 N*s`, mass `2 kg`, and 30-degree thrust direction produced:
+
+```text
+delta_v = 5 (cos(30 deg), sin(30 deg)) m/s
+```
+
+to floating-point precision despite an awkward `0.7 s` outer timestep crossing multiple curve knots and burnout.
+
+The launchable default curve's independent trapezoids sum to `17.58 N*s`; its first `0.01 s` delivers `0.136 N*s` upward versus `0.0981 N*s` downward gravity impulse, producing the expected free-flight numerical endpoint `vy=0.0379 m/s`, `y=0.000379 m` without pad/contact physics.
+
+For a separate nontrivial sampled curve with active drag, a test-local independent RK4 reference at `t=0.6 s` was:
+
+```text
+position = (2.086955589988, 100.340594347210) m
+velocity = (4.360834957988, -0.023157593980) m/s
+```
+
+| `dt` (s) | position-vector error (m) | velocity-vector error (m/s) |
+| ---: | ---: | ---: |
+| 0.020 | 0.0261762225 | 0.0046348364 |
+| 0.010 | 0.0136805265 | 0.0024161277 |
+| 0.005 | 0.0068400396 | 0.0012071078 |
+
+Position-error ratios were approximately `1.913` and `2.000`; velocity-error ratios were approximately `1.918` and `2.002`.
+
+### Interpretation and uncertainty
+
+The isolated impulse result shows that propulsion impulse, not timestep sampling, determines the constant-mass thrust-only velocity change. The active-drag evidence is consistent with first-order convergence for the selected stable case. Exact motor impulse does not make position, drag impulse, apogee, or impact exact.
+
+Curve knots are numerical drag boundaries. A redundant collinear sample can add a drag reevaluation and slightly alter finite-timestep trajectory even while preserving the mathematical thrust curve and total impulse. The default data is synthetic educational data, not real-motor validation.
diff --git a/docs/VALIDATION.md b/docs/VALIDATION.md
index 0036d07..8ac68b6 100644
--- a/docs/VALIDATION.md
+++ b/docs/VALIDATION.md
@@ -5 +5 @@
-RocketSim validates simple cases against independently calculated answers before relying on integrated flight behavior. Expected force values and analytical trajectories in tests are calculated directly from literal parameters and equations, not by calling the production drag or force-breakdown helpers. A finer production run is not used as the sole nonlinear oracle.
+RocketSim validates simple cases against independently calculated answers before relying on integrated flight behavior. Expected force values, thrust interpolation, impulse, motor metrics, and analytical trajectories in tests are calculated directly from literal parameters and equations, not by calling production curve, drag, or force-breakdown helpers. A finer production run is not used as the sole nonlinear oracle.
@@ -15 +15 @@ conda run -n rocketsim python -m pytest
-Prompt 02 gravity/thrust tests explicitly set air density to zero when their references assume constant acceleration. They retain force signs, the half-open burn predicate, semi-implicit update ordering, exact non-aligned burnout split, constant-mass behavior, analytical gravity/powered/piecewise motion, the known constant-acceleration position-error identity, ground interpolation, reset, strict accumulator semantics, and display-FPS independence.
+Prompt 02 gravity/thrust tests explicitly use a two-sample constant-thrust curve and set air density to zero when their references assume constant acceleration. They retain force signs, the half-open burn predicate, semi-implicit update ordering, exact non-aligned burnout split, constant-mass behavior, analytical gravity/powered/piecewise motion, the known constant-acceleration position-error identity, ground interpolation, reset, strict accumulator semantics, and display-FPS independence.
@@ -18,0 +19,60 @@ An additional integrated analytical case independently verifies that each of `rh
+## Sampled propulsion data and metrics
+
+Independent tests cover:
+
+- immutable sample and curve ownership;
+- finite, non-negative samples;
+- exact first time zero and strictly increasing later times;
+- duplicate/decreasing/empty rejection;
+- the single-sample `(0,0)` zero-duration limit;
+- exact stored values at interior knots;
+- literal midpoint interpolation on rising and falling intervals;
+- zero thrust before ignition and at/after the half-open burn end;
+- a nonzero final stored sample that contributes to the last trapezoid while instantaneous burn-end thrust is zero;
+- triangle, rectangle, and multi-segment total impulse;
+- partial and cross-segment delivered impulse;
+- delivered-impulse monotonicity and interval additivity;
+- constant- and zero-thrust factories; and
+- independently calculated average and peak thrust.
+
+The launchable synthetic default is:
+
+```text
+(0.00 s, 12 N)
+(0.05 s, 28 N)
+(0.12 s, 24 N)
+(0.35 s, 20 N)
+(0.70 s, 16 N)
+(0.95 s,  8 N)
+(1.05 s,  0 N)
+```
+
+Literal trapezoid areas are `1.00`, `1.82`, `5.06`, `6.30`, `3.00`, and `0.40 N*s`, giving:
+
+```text
+burn duration  1.05 s
+total impulse  17.58 N*s
+peak thrust    28 N
+average thrust 16.742857142857... N
+```
+
+The originally proposed zero-at-ignition curve retains independently verified `17.28 N*s` total impulse in an airborne, zero-gravity, zero-drag case. It is not used as the ground-launch default because its first `0.01 s` interval delivers only `0.028 N*s` upward while gravity delivers `0.0981 N*s` downward.
+
+## Exact propulsion impulse and knot boundaries
+
+One-knot and multi-knot tests use literal impulse and position oracles, so a whole-step method that happens to deliver the right final velocity cannot conceal missing internal segmentation. One `0.5 s` outer step crossing `0.1`, `0.2`, and `0.3 s` knots produces exactly one state at each knot, increments the outer step count once, and reaches the independently derived `vx=1.2 m/s`, `x=0.31 m` result.
+
+A constant `4 N` curve ending at the non-grid-aligned time `0.35 s` with `dt=0.2 s` delivers exactly `1.4 N*s`, creates one POWERED-to-COAST transition, reports zero instantaneous thrust at burnout, and ends the second outer step at `vx=1.4 m/s`, `x=0.44 m` with no excess thrust.
+
+With gravity and drag disabled, a literal `10 N*s` curve, `m=2 kg`, and a fixed 30-degree direction produces exactly the independent vector result:
+
+```text
+delta_v = 5 (cos(30 deg), sin(30 deg)) m/s
+```
+
+This validates motor impulse–momentum without using production total-impulse helpers as the oracle.
+
+With active drag, a literal first segment uses `J_T=0.4 N*s`, independently calculated start drag `(-1.875,-2.5) N`, and gravity `(0,-6) N` to reach `v=(3.10625,3.575) m/s` and `p=(1.310625,10.3575) m`. Resulting-state telemetry then uses instantaneous `T(0.1)=6 N` and drag recalculated from that resulting velocity, proving that segment-average thrust is not displayed as current thrust.
+
+An additional multi-knot active-drag case independently verifies that drag is reevaluated at every curve knot. This is why the configured knot set is documented as part of the numerical mesh.
+
@@ -88,0 +149,19 @@ Velocity error ratios as timestep halves are approximately `1.992` and `1.996`;
+## Sampled-thrust active-drag convergence
+
+A test-local standard-library RK4 oracle independently implements literal sampled thrust, gravity, and quadratic drag. It does not call production interpolation, force, impulse, or stepping helpers. At `t=0.6 s`, its reference is:
+
+```text
+position = (2.086955589988, 100.340594347210) m
+velocity = (4.360834957988, -0.023157593980) m/s
+```
+
+Production errors for the same immutable knot set were:
+
+| `dt` (s) | position-vector error (m) | velocity-vector error (m/s) |
+| ---: | ---: | ---: |
+| 0.020 | 0.0261762225 | 0.0046348364 |
+| 0.010 | 0.0136805265 | 0.0024161277 |
+| 0.005 | 0.0068400396 | 0.0012071078 |
+
+Position-error ratios were approximately `1.913` and `2.000`; velocity-error ratios were approximately `1.918` and `2.002`. This is measured evidence consistent with first-order convergence for the selected stable case. Separate zero-gravity/zero-drag runs at all three timesteps reproduce the exact literal motor-impulse velocity to roundoff, isolating the remaining numerical error to position and velocity-dependent drag treatment.
+
@@ -107,0 +187 @@ The suite verifies:
+- equal state, trajectory, force telemetry, and delivered impulse for the sampled default with active drag partitioned at 30, 60, and 144 FPS through the public accumulator;
@@ -121,0 +202,4 @@ Automated evidence covers:
+- Inspector current thrust, motor phase, burn-time progress, duration, peak/average thrust, delivered/total impulse, and time-varying thrust/impulse equations;
+- timeline geometry derived from the configured production curve's exact samples and current simulation time;
+- timeline cursor clamping that is explicitly labeled after burnout rather than misrepresented as coast simulation time;
+- production-curve identity reaching the renderer without a second curve, interpolation, or trapezoid implementation;
@@ -133 +217 @@ Visual inspection supplements these automated checks but is not the scientific o
-## Current Prompt 03 suite result
+## Prompt 03 historical suite result
@@ -141 +225,11 @@ After specialist review corrections, the complete suite reports:
-Focused aerodynamic, analytical, convergence, integration, lifecycle, timing, and rendering groups also pass independently, as does the bounded SDL dummy application smoke test.
+Prompt 03 completed with 119 passing tests. Prompt 04 preserves those contracts through constant and zero sampled-curve limiting cases.
+
+## Current Prompt 04 suite result
+
+After post-implementation specialist corrections, the complete implementation and documentation-development suite reports:
+
+```text
+162 passed
+```
+
+Focused propulsion, impulse, knot, active-drag, convergence, lifecycle, accumulator, rendering, and Living Course executable-contract groups pass independently.
@@ -158,0 +253 @@ Focused aerodynamic, analytical, convergence, integration, lifecycle, accumulato
+Focused propulsion unit, propulsion integration, sampled-thrust convergence, FPS/reset, and timeline/Inspector tests are also run separately.
@@ -162 +257 @@ Focused aerodynamic, analytical, convergence, integration, lifecycle, accumulato
-The evidence establishes correctness for the documented still-air, constant-property, isotropic point-mass drag approximation and its numerical contract. It does not establish real-world aerodynamic accuracy. Landing values remain timestep-sensitive. Real-flight comparison requires measured vehicle data, calibration kept separate from evaluation, and explicit uncertainty analysis.
+The evidence establishes correctness for the documented synthetic piecewise-linear propulsion representation and still-air, constant-property, isotropic point-mass drag approximation. Exact curve impulse does not make position, drag impulse, apogee, or impact exact. Ground admission and landing remain timestep-sensitive discrete-event approximations. The default curve is not measured motor data. Real-flight comparison requires measured vehicle/motor data, calibration kept separate from evaluation, and explicit uncertainty analysis.
diff --git a/docs/decisions/decision_02_constant_thrust_state_model.md b/docs/decisions/decision_02_constant_thrust_state_model.md
index d3b1d5e..2d318e9 100644
--- a/docs/decisions/decision_02_constant_thrust_state_model.md
+++ b/docs/decisions/decision_02_constant_thrust_state_model.md
@@ -37,0 +38,4 @@ No prior decision is superseded.
+
+## Later partial supersession
+
+Decision 07 supersedes this record's independently configured constant-thrust/burn-duration propulsion representation and its `20 N` / `1 s` default. The constant-mass state representation, fixed world thrust direction, half-open motor interval, ground-boundary policy, and instantaneous resulting-state telemetry remain accepted. The two-sample rectangular `ThrustCurve` preserves the former constant-thrust model as a limiting case.
diff --git a/docs/decisions/decision_06_living_rocketry_course.md b/docs/decisions/decision_06_living_rocketry_course.md
new file mode 100644
index 0000000..30614c3
--- /dev/null
+++ b/docs/decisions/decision_06_living_rocketry_course.md
@@ -0,0 +1,51 @@
+# Decision 06: Living Rocketry Course
+
+- Date: 2026-08-29
+- Status: accepted
+- Related prompt: `docs/prompts/prompt_04_propulsion_learning.md`
+- Supersedes: none
+
+## Decision
+
+RocketSim is both a scientifically inspectable simulator and an educational environment for learning rocketry. Maintain one learner-facing course at:
+
+```text
+docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
+```
+
+Every approved milestone that changes implemented physics, propulsion, scientifically meaningful numerical interpretation, events/phases, Physics Inspector content, educational visualization, learner controls, or simulator experiments must perform a Living Course impact review before completion. The parent agent must update applicable material without waiting for a future prompt to request it, including revising earlier lessons when a later model supersedes or qualifies an earlier simplification.
+
+Scientific truth remains in `docs/PHYSICS_MODEL.md`; validation methodology and evidence remain in `docs/VALIDATION.md`. The course is the pedagogical projection of those sources and actual simulator behavior, not an independent physics authority.
+
+The course uses a progressive prediction → observation → explanation approach, distinguishes real-world nature from RocketSim's approximation, states assumptions and limits, supplies reproducible hands-on activities, and includes reasoning-based checks for understanding. A read-only `learning_reviewer` reviews the complete course before any affected milestone completes.
+
+## Context and problem
+
+RocketSim already exposes forces, equations, phases, and numerical state, but developer-facing documentation alone does not teach a learner how to connect those quantities. A course appended only when explicitly requested would become stale as models, controls, and visualizations evolve. An educational product identity therefore needs a durable repository policy and a retroactive maintenance rule.
+
+## Options considered
+
+- Maintain one living tutorial tied to authoritative scientific documentation and implementation.
+- Write a one-time Prompt 04 propulsion tutorial with no future maintenance requirement.
+- Treat developer documentation as the learner course.
+- Split immediately into many chapter files and a course framework.
+
+## Rationale
+
+One coherent document is easy to discover, review, and revise at the current project size. Explicit source-of-truth boundaries prevent pedagogical wording from silently redefining equations or evidence. Whole-course specialist review catches older chapters made obsolete by later physics. Prediction, observation, and explanation turns the simulator into an interactive laboratory rather than a passive animation.
+
+## Consequences and tradeoffs
+
+- Physics and educational milestones acquire a course-impact and learning-review completion gate.
+- Course updates may touch older lessons even when a milestone adds a new later topic.
+- Activities must match actual controls and configurations; future features may be named only as unimplemented.
+- Automated behavior tests protect concrete UI/data contracts, but scientific and pedagogical prose remains primarily a specialist-review responsibility.
+- The course adds maintenance work and must not duplicate or replace authoritative physics and validation documents.
+
+## Related prompt records
+
+- `docs/prompts/prompt_04_propulsion_learning.md`
+
+## Superseding decision
+
+None.
diff --git a/docs/decisions/decision_07_sampled_thrust_curve_model.md b/docs/decisions/decision_07_sampled_thrust_curve_model.md
new file mode 100644
index 0000000..93034cb
--- /dev/null
+++ b/docs/decisions/decision_07_sampled_thrust_curve_model.md
@@ -0,0 +1,81 @@
+# Decision 07: Sampled thrust-curve propulsion model
+
+- Date: 2026-08-29
+- Status: accepted
+- Related prompt: `docs/prompts/prompt_04_propulsion_learning.md`
+- Supersedes: Decision 02's independently configured propulsion representation and default; its state model and other physical provisions remain accepted
+
+## Decision
+
+Prompt 04 replaces independently configurable constant thrust and burn duration with one immutable, authoritative piecewise-linear `ThrustCurve`. The curve owns validated `(time_s, thrust_n)` samples, begins at exactly zero time, uses strictly increasing later times, and derives burn duration from its final sample. The zero-duration limit is the single sample `(0,0)`.
+
+Instantaneous thrust is linearly interpolated for `0 <= t < burn_end`, equals stored values at interior knots, and is zero before ignition and at/after burn end. A final nonzero stored sample remains the left-limit endpoint of the last trapezoid even though instantaneous thrust at exact burn end is zero.
+
+Total and delivered motor impulse are exact geometric integrals of the stored curve. Average thrust is total impulse divided by positive burn duration, and stored peak thrust is the maximum sample ordinate—the represented curve's supremum. A unique nonzero terminal peak is a left-limit value rather than an attained value of the half-open instantaneous function. A two-sample rectangle is the Prompt 02–03 constant-thrust limit; the singleton zero curve is the zero-thrust limit.
+
+Every fixed outer physics step is split at all strictly crossed curve knots. On each internal segment:
+
+```text
+J_T = exact piecewise-linear thrust impulse
+F_other_start = F_gravity + F_drag(v_start)
+
+v_next = v_start
+         + (J_T / m) (cos(theta), sin(theta))
+         + (F_other_start / m) dt
+
+p_next = p_start + v_next dt
+```
+
+Current force and acceleration telemetry remains instantaneous at the resulting time and velocity. Mass and thrust direction remain constant.
+
+The default is self-authored synthetic educational data:
+
+```text
+(0.00 s, 12 N)
+(0.05 s, 28 N)
+(0.12 s, 24 N)
+(0.35 s, 20 N)
+(0.70 s, 16 N)
+(0.95 s,  8 N)
+(1.05 s,  0 N)
+```
+
+It has `17.58 N*s` total impulse, `28 N` peak thrust, and `16.742857... N` average thrust. It begins above the default rocket's weight so the ground launch is admissible without pad/contact support. The originally proposed zero-at-ignition curve remains an airborne/zero-gravity educational validation example with `17.28 N*s`, not the ground default.
+
+## Context and problem
+
+The prior rectangular motor delivered correct constant thrust but could not represent ignition rise, changing thrust, peak versus average thrust, or motor impulse. Time-varying thrust also creates discontinuous interpolation slopes and knot boundaries that a start-value-only force evaluation would integrate incorrectly.
+
+The proposed zero-at-ignition default delivers only `0.028 N*s` in the first `0.01 s`, less than the `0.0981 N*s` downward gravity impulse. Under the accepted no-pad/no-contact model, it would move below ground. Adding a clamp, hidden hold, or normal force would introduce a second physical effect. The launchable `12 N` initial sample is the smallest transparent scope correction; zero-at-ignition behavior remains demonstrable away from the ground boundary.
+
+## Options considered
+
+- Exact piecewise-linear impulse with internal knot segmentation, the selected model.
+- Evaluate instantaneous thrust only at segment start, rejected because rising/falling impulse error becomes timestep-dependent.
+- Add pad hold/release or normal-force physics, rejected as a new contact model outside Prompt 04.
+- Preserve the original ground default through look-ahead, clamping, or discarded downward steps, rejected as hidden physics.
+- Use an above-ground default, rejected because it would evade rather than resolve the intended launch scenario.
+- Adopt a general motor database/import/plugin framework, rejected as unnecessary scope.
+
+## Rationale
+
+One immutable curve removes competing propulsion sources of truth. Exact trapezoidal impulse is analytically inspectable and makes the impulse–momentum limiting case independent of timestep. Knot splitting handles every curve interval and burn end deterministically while retaining the established fixed outer clock, semi-implicit position update, and explicit start-velocity drag.
+
+The adjusted default keeps the intended synthetic shape, peak, and duration while remaining honest about the absence of launch support physics. Its metrics are independently derived and displayed from production data.
+
+## Consequences and tradeoffs
+
+- Motor impulse is exact for each completed segment of the stored polyline, but position, drag impulse, apogee, and impact remain numerical approximations.
+- Curve knots become internal numerical boundaries. Redundant collinear samples can cause extra drag reevaluations and change a finite-timestep active-drag trajectory even when the mathematical thrust curve is unchanged.
+- The outer accumulator and physics-step count remain based on the configured fixed timestep; internal knot states may add trajectory samples.
+- Powered phase is the curve's half-open time interval, not a guarantee of positive instantaneous thrust.
+- Ground impact remains interpolation of the discrete path; a powered impact is not an exact partial-impulse event solution.
+- The model omits variable mass, propellant depletion, specific impulse, exhaust velocity, motor chemistry, measured motor import, and thrust-vector control.
+
+## Related prompt records
+
+- `docs/prompts/prompt_04_propulsion_learning.md`
+
+## Superseding decision
+
+Decision 07 partially supersedes Decision 02 as stated above. Decision 02's constant-mass state model, fixed thrust direction, ground-boundary policy, and resulting-state telemetry remain accepted.
diff --git a/docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md b/docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
new file mode 100644
index 0000000..3ce5cce
--- /dev/null
+++ b/docs/learning/LEARNING_ROCKETRY_WITH_ROCKETSIM.md
@@ -0,0 +1,741 @@
+# Learning Rocketry with RocketSim
+
+RocketSim is your physics laboratory. It lets you predict a rocket's motion, observe the modeled forces and state, and explain why the motion followed. It is deliberately simple enough that every displayed quantity can be connected to an equation.
+
+This course is written for a motivated high-school student or beginning undergraduate who knows basic algebra. Physical intuition comes first; vectors, equations, and numerical evidence follow.
+
+You do not need prior calculus. A few supplied symbols are reading aids: `pi/2 rad` means `90 degrees`; `u_T` is a unit vector that points in the thrust direction; an integral means accumulated graph area; and `tanh` is a Python/calculator function used for one validation reference whose derivation is beyond this introductory course.
+
+RocketSim is not a certified launch predictor. Its value is that its assumptions are visible and testable.
+
+## How to use this course
+
+Most activities follow this rhythm:
+
+```text
+Predict → Observe → Explain
+```
+
+Before running an activity, write down what you expect. During the run, record actual numbers and signs. Afterward, use forces and equations—not visual plausibility alone—to explain the result.
+
+Scientific truth for the implemented model lives in `docs/PHYSICS_MODEL.md`. Validation methods and quantitative evidence live in `docs/VALIDATION.md`. This course explains those sources for learners.
+
+---
+
+# Part I — Foundations
+
+## 1. RocketSim as a Physics Laboratory
+
+### What are we trying to understand?
+
+How can a simulator help us learn physics without confusing a mathematical model with nature?
+
+### Physical intuition
+
+A rocket animation can look convincing and still be wrong. A scientific simulation should let you ask:
+
+- Which forces are active?
+- What values and units do they have?
+- Which equation combines them?
+- Which assumptions were omitted?
+- Does a simpler case agree with an answer we can derive independently?
+
+RocketSim exposes those questions through its Physics Inspector, force arrows, motor timeline, and deterministic stepping.
+
+### REAL-WORLD PHYSICS
+
+A real rocket rests on a launch pad or rail, burns propellant, moves through changing atmosphere, rotates, and may deploy recovery hardware. Measurements have uncertainty. A drawing of a rocket also has an attitude and shape.
+
+### ROCKETSIM MODEL
+
+The current rocket is a constant-mass point in a flat 2D world. It has no pad-support or rail force, no rotation, and no recovery system. The rocket-shaped marker shows position; its drawn orientation is not simulated attitude.
+
+Before launch, READY deliberately displays inactive zero forces and zero stored acceleration. This is an interface state, not a claim that gravity disappeared or that a solved pad equilibrium exists.
+
+### Controls
+
+```text
+SPACE  launch; pause or resume a live flight
+RIGHT  advance one outer physics step only while a live flight is paused
+R      reset the complete deterministic run
+F      show or hide force vectors
+I      show or hide the Physics Inspector
+ESC    exit
+```
+
+There is no parameter editor. `F` and `I` change presentation only. `RIGHT` does not act while READY, while running, or after landing.
+
+### Try it in RocketSim
+
+Run:
+
+```bash
+conda run -n rocketsim python -m rocket_sim
+```
+
+#### Predict
+
+Will hiding force arrows or the Inspector change the trajectory? Will reset produce the same run?
+
+#### Observe
+
+1. Press `SPACE` to launch.
+2. Press `F`, then `I`, while the rocket flies.
+3. Press `R` after part or all of the flight.
+4. Repeat the same launch.
+5. If `F` or `I` left an overlay hidden, press that key again before continuing so both force vectors and the Inspector are visible.
+
+#### Explain
+
+The renderer reads simulation state but cannot modify it. Reset restores state, trajectory, outer-step count, and fractional wall-time accumulator. It does not reset the renderer's `F` or `I` visibility toggles. The same configuration and elapsed-time sequence is deterministic.
+
+### Check your understanding
+
+1. Why is plausible animation insufficient evidence of correctness?
+2. Why do READY's zero displayed forces not mean gravity ceased to exist?
+3. What result would reveal that `F` or `I` had incorrectly changed physics?
+
+---
+
+## 2. Position, Velocity, and Acceleration
+
+### Physical intuition
+
+Position says where the rocket is. Velocity says how quickly and in which direction position is changing. Acceleration says how quickly velocity is changing.
+
+A rocket can move upward while accelerating downward. That is exactly what happens during much of coast: upward velocity is being reduced by gravity and drag.
+
+### Coordinate system and units
+
+RocketSim uses SI units internally:
+
+```text
++x  right
++y  upward
+ground y = 0
+
+position      metres (m)
+velocity      metres per second (m/s)
+acceleration  metres per second squared (m/s^2)
+time          seconds (s)
+```
+
+Pygame screen coordinates increase downward. Only the renderer performs that inversion; stored world `+y` remains upward.
+
+For a velocity vector:
+
+```text
+v = (vx, vy)
+speed = |v| = sqrt(vx^2 + vy^2)
+```
+
+Velocity contains direction; speed does not.
+
+### Try it in RocketSim
+
+#### Predict
+
+During coast ascent, what signs should `vy` and `ay` have?
+
+#### Observe
+
+1. Launch with `SPACE`.
+2. Pause during upward coast with `SPACE`.
+3. Record time, altitude, `vy`, speed, and `ay`.
+4. Press `RIGHT` several times. Each press advances the configured `0.01 s` outer step and leaves the flight paused.
+
+#### Explain
+
+During upward coast, `vy > 0` while gravity and downward drag normally make `ay < 0`. The rocket is rising more slowly each step. Displayed endpoint acceleration is the instantaneous acceleration at that endpoint, not necessarily the exact average acceleration over the preceding step.
+
+### Check your understanding
+
+1. Can velocity be upward while acceleration is downward?
+2. Can acceleration be zero while velocity is nonzero?
+3. Why does screen-coordinate inversion not change the sign convention in the physics equations?
+
+---
+
+## 3. Forces and Newton's Second Law
+
+### Physical intuition
+
+A force changes momentum. Several forces can act at once, so direction matters. RocketSim adds force vectors and then divides their net by the constant mass.
+
+Momentum is the vector
+
+```text
+p = m v
+```
+
+with units `kg*m/s`. Impulse changes momentum, and `1 N*s = 1 kg*m/s`.
+
+### Governing equations
+
+```text
+F_net = sum of forces
+a = F_net / m
+```
+
+Force uses newtons:
+
+```text
+1 N = 1 kg*m/s^2
+```
+
+The current forces are:
+
+```text
+F_net = F_thrust + F_gravity + F_drag
+```
+
+The Inspector shows components and magnitudes. Arrow lengths use one rendering-only pixels-per-newton scale; their positions and labels may be moved for readability without changing physical direction or magnitude.
+
+### REAL-WORLD PHYSICS
+
+Real rockets may also experience pad contact, rail forces, lift, aerodynamic moments, and recovery forces.
+
+### ROCKETSIM MODEL
+
+Only thrust, gravity, and quadratic drag are simulated. There is no hidden damping or “game feel” force.
+
+### Try it in RocketSim
+
+#### Predict
+
+If the upward thrust arrow is longer than the downward gravity arrow, must acceleration be upward?
+
+#### Observe
+
+Pause during flight. Add the displayed x components and y components of thrust, gravity, and drag. Compare with displayed net force. Divide net components by the displayed `1.000 kg` mass and compare with acceleration. Small differences can appear because the Inspector rounds displayed decimals.
+
+#### Explain
+
+Thrust versus weight alone is not the full comparison once drag has a significant component. Newton's second law uses the complete vector sum.
+
+### Check your understanding
+
+1. What does zero net force imply about acceleration?
+2. What does zero net force not imply about velocity?
+3. Why can a large thrust coexist with downward acceleration in a nonvertical or high-drag situation?
+
+---
+
+## 4. Powered Flight
+
+### Physical intuition
+
+A motor pushes exhaust one way and the rocket gains momentum the other way. RocketSim does not model exhaust or combustion. It accepts a thrust magnitude versus time and applies it in one fixed world direction.
+
+### Governing equations
+
+```text
+u_T = (cos(theta), sin(theta))
+F_T(t) = T(t) u_T
+F_g = (0, -m g)
+```
+
+The default launch is vertical, so `theta = pi/2`. The default rocket mass is `1 kg`; its weight magnitude is:
+
+```text
+m g = (1 kg)(9.81 m/s^2) = 9.81 N
+```
+
+The default curve begins at `12 N`, so its free-flight initial vertical net force is positive before drag grows.
+
+### REAL-WORLD PHYSICS
+
+Real rockets lose mass as propellant burns. Their thrust direction follows the nozzle and changing attitude. A launch rail constrains early motion and supports the rocket before release.
+
+### ROCKETSIM MODEL
+
+Mass is constant. Thrust direction is fixed in world coordinates. There is no rail, pad reaction, hold-down, rotation, or thrust-vector control.
+
+The launchable default starts above weight because a motor that begins at zero thrust would initially fall into the ground under this no-contact model. A separate airborne example in Lesson 9 safely demonstrates zero thrust at exact ignition.
+
+### Try it in RocketSim
+
+#### Predict
+
+Must maximum acceleration occur at the same time as maximum thrust?
+
+#### Observe
+
+Launch, pause during the declining portion of the motor timeline, and compare current thrust, weight, drag, net force, and acceleration. Single-step and watch thrust fall while it remains nonzero.
+
+#### Explain
+
+Acceleration depends on all active forces. As speed changes, drag changes. Peak thrust and peak acceleration therefore need not occur at the same time.
+
+### Check your understanding
+
+1. Why is `T > mg` incomplete for an angled launch with drag?
+2. Which RocketSim assumption keeps the thrust direction unchanged?
+3. What important launch-pad physics is absent?
+
+---
+
+## 5. Burnout, Coast, and Apogee
+
+### Physical intuition
+
+Burnout means motor thrust ends. It does not mean velocity instantly becomes zero. Momentum carries the rocket upward while gravity and drag reduce its upward velocity.
+
+### Motor and flight phases
+
+The motor interval is half-open:
+
+```text
+0 <= t < burn_end  ACTIVE motor interval
+t >= burn_end      motor COMPLETE; instantaneous thrust zero
+```
+
+The flight uses READY, POWERED, COAST, and LANDED. POWERED describes the configured motor-time interval; it does not guarantee `T(t) > 0` at every possible sample.
+
+At apogee in a purely vertical flight:
+
+```text
+vy = 0 momentarily
+```
+
+Gravity is not zero. Drag is zero at exactly zero air-relative speed, so the rocket accelerates downward. Apogee is not a separate displayed phase in the current simulator.
+
+### Try it in RocketSim
+
+#### Predict
+
+What will happen to thrust, velocity, and acceleration at burnout?
+
+#### Observe
+
+1. Pause anywhere during the declining burn.
+2. Press `RIGHT` through the burnout boundary.
+3. Watch current thrust, motor phase, delivered impulse, net force, acceleration, velocity, and the trajectory color.
+4. Resume and observe coast toward apogee.
+
+#### Explain
+
+Instantaneous thrust is exactly zero at the half-open endpoint. Total impulse stays fixed at its final value, and velocity remains continuous. A curve with a nonzero final left-limit thrust can produce an acceleration jump at burnout. The default curve instead tails continuously to zero, although its motor and flight phases still change at the endpoint.
+
+Ground return is found by interpolating the first descending discrete segment that crosses `y=0`. It is not an exact continuous collision solution and there is no motion after impact.
+
+### Check your understanding
+
+1. Why can the rocket continue upward after burnout?
+2. Which quantities are zero at vertical apogee, and which are not?
+3. Why is impact time still timestep-sensitive?
+
+---
+
+## 6. Aerodynamic Drag
+
+### Physical intuition
+
+Moving through air pushes air aside. The air pushes back opposite the rocket's velocity relative to the air. Faster motion produces much more drag in the quadratic model.
+
+### Governing equation
+
+```text
+v_air = v_rocket_ground - v_air_ground
+
+F_drag = -0.5 rho Cd A |v_air| v_air
+```
+
+Units and meanings:
+
+```text
+rho  air density                 kg/m^3
+Cd   drag coefficient            dimensionless
+A    effective reference area    m^2
+v_air air-relative velocity      m/s
+```
+
+The vector form gives magnitude:
+
+```text
+|F_drag| = 0.5 rho Cd A speed^2
+```
+
+If speed doubles, drag magnitude becomes four times as large. At zero air-relative speed, drag is exactly zero. The minus sign makes drag oppose the complete velocity vector in every direction.
+
+### REAL-WORLD PHYSICS
+
+Atmospheric density varies with altitude and weather. Wind changes air-relative velocity. `Cd` and effective area can vary with Mach number, Reynolds number, attitude, and shape.
+
+### ROCKETSIM MODEL
+
+Air is still. Density, `Cd`, and one direction-independent effective area remain constant. The default values are educational, not calibrated vehicle measurements:
+
+```text
+rho = 1.225 kg/m^3
+Cd  = 0.75
+A   = 0.01 m^2
+```
+
+### Try it in RocketSim
+
+#### Predict
+
+Which direction should drag point during vertical ascent? During vertical descent?
+
+#### Observe
+
+Use `F` to show arrows. Observe drag during powered ascent, coast ascent, and descent. Pause and compare the sign of `vy` with the sign of vertical drag.
+
+#### Explain
+
+During ascent, air-relative velocity points upward and drag points downward. During descent, velocity points downward and drag points upward. In general 2D motion, say “opposite the velocity vector,” not merely “up” or “down.”
+
+### Check your understanding
+
+1. Why does doubling speed quadruple drag magnitude in this model?
+2. Why is drag zero at zero air-relative speed?
+3. How would wind change `v_air`, even though wind is not implemented?
+
+---
+
+## 7. Terminal Velocity
+
+### Physical intuition
+
+As a falling object speeds up, upward drag grows. Eventually drag can balance weight. Then net acceleration is zero while the object continues downward at nonzero velocity.
+
+For vertical unpowered descent:
+
+```text
+F_drag + F_g = 0
+```
+
+For positive `m`, `g`, `rho`, `Cd`, and `A`, the modeled terminal-speed magnitude is:
+
+```text
+v_terminal = sqrt(2 m g / (rho Cd A))
+```
+
+The velocity vector at downward equilibrium is `(0, -v_terminal)`.
+
+Terminal velocity is an equilibrium approached by the equations, not a speed clamp. The default flight is not claimed to reach it.
+
+### Headless laboratory activity
+
+The current UI has no parameter editor, so use this complete tested configuration from the repository root:
+
+```bash
+conda run --no-capture-output -n rocketsim python - <<'PY'
+import math
+
+from rocket_sim import Simulation, SimulationConfig, ThrustCurve, Vector2
+
+simulation = Simulation(
+    SimulationConfig(
+        mass_kg=2.0,
+        thrust_curve=ThrustCurve.zero(),
+        gravity_m_s2=8.0,
+        air_density_kg_m3=2.0,
+        drag_coefficient=1.0,
+        reference_area_m2=1.0,
+        physics_dt_s=0.005,
+        initial_position_m=Vector2(0.0, 100.0),
+    )
+)
+simulation.launch()
+for _ in range(200):
+    simulation.step()
+
+expected_vy = -4.0 * math.tanh(2.0)
+print("simulated vy:", simulation.state.velocity_m_s.y)
+print("analytical vy:", expected_vy)
+print("terminal-speed magnitude:", 4.0)
+PY
+```
+
+#### Predict
+
+At `t=1 s`, should the downward speed already equal `4 m/s`, or still be approaching it?
+
+#### Observe and explain
+
+Compare numerical and analytical values. The remaining difference contains fixed-timestep numerical error. The constant-density terminal speed is a statement about this model, not a measured real rocket.
+
+### Check your understanding
+
+1. Can acceleration be zero while velocity is nonzero?
+2. What force direction restores a fall faster than terminal speed?
+3. Why does the model's terminal speed not establish a real rocket's terminal speed?
+
+---
+
+## 8. Current Model Limitations
+
+Scientific modeling means knowing what was left out.
+
+| REAL-WORLD PHYSICS | CURRENT ROCKETSIM MODEL |
+| --- | --- |
+| Rocket rests on a pad/rail before liftoff | No support, rail, hold-down, or normal-force model |
+| Motors consume propellant | Mass remains constant |
+| Motor curves may be measured with uncertainty | Default curve is a self-authored synthetic polyline |
+| Thrust direction follows attitude/nozzle | Fixed world direction |
+| Atmosphere changes with altitude/weather | Constant density and still air |
+| Wind changes air-relative velocity | No wind |
+| `Cd` and area depend on flow and attitude | Constant `Cd`, isotropic effective area |
+| Rockets rotate and have stability dynamics | 2D point mass; no rotation, CG, or CP |
+| Lift and compressibility may matter | No lift, Mach, Reynolds, or compressibility effects |
+| Recovery and contact dynamics occur | Interpolated terminal ground event; no recovery or bounce |
+| Continuous dynamics | Fixed outer timestep with internal knot segments |
+| Measurements and calibration have uncertainty | No calibration or uncertainty model |
+
+Semi-implicit position stepping and explicit start-velocity drag are numerical approximations. Exact motor impulse does not make position, apogee, landing time, or impact exact. The stored knot set is part of the numerical configuration: redundant collinear knots leave the thrust polyline and impulse unchanged but cause extra drag and position updates, so an active-drag trajectory can differ slightly. Extreme timestep/speed combinations can make explicit quadratic-drag integration unstable; RocketSim applies no arbitrary clamp to hide that.
+
+Results are not 3D flight dynamics, engineering certification, or safety advice.
+
+### Check your understanding
+
+1. Which missing effect would change mass during the burn?
+2. Which missing effects would make the thrust direction change?
+3. Why should an educational default curve never be called real motor data?
+
+---
+
+# Part II — Propulsion
+
+## 9. Rocket Motors, Thrust Curves, and Impulse
+
+### What are we trying to understand?
+
+How does thrust that changes with time build momentum, and why are peak thrust, average thrust, and total impulse different?
+
+### Physical intuition
+
+Thrust is a force at an instant. Impulse measures force accumulated over time. On a thrust-versus-time graph, motor impulse is the area under the curve.
+
+Two curves can reach the same peak but enclose different areas. Two curves can enclose the same area but deliver it at different times. With drag active, different delivery timing can create different trajectories because speed—and therefore drag—changes along the way.
+
+### REAL-WORLD PHYSICS
+
+Real motor thrust changes during ignition, pressure rise, propellant burn, and tail-off. Real curves are measured, have sampling and measurement uncertainty, and can contain features missed by sparse data. The rocket also loses propellant mass.
+
+### ROCKETSIM MODEL
+
+RocketSim stores immutable samples and joins adjacent points with straight lines. The default samples are self-authored educational data:
+
+| time (s) | thrust (N) |
+| ---: | ---: |
+| 0.00 | 12 |
+| 0.05 | 28 |
+| 0.12 | 24 |
+| 0.35 | 20 |
+| 0.70 | 16 |
+| 0.95 | 8 |
+| 1.05 | 0 |
+
+This is not a commercial, measured, or certified motor.
+
+Mass remains exactly `1 kg` in the default run. There is no propellant depletion, mass flow, specific impulse, exhaust velocity, chamber pressure, nozzle model, or combustion chemistry.
+
+### Sampled interpolation
+
+Between adjacent samples:
+
+```text
+T(t) = T_i
+       + (T_(i+1) - T_i)
+         (t - t_i) / (t_(i+1) - t_i)
+```
+
+Boundary rules are:
+
+```text
+T(t) = 0 for t < 0
+T(t_i) = stored T_i at interior knots
+T(t) = 0 for t >= burn_end
+burn interval = [0, burn_end)
+```
+
+The motor phase is based on time, not on whether a particular instantaneous value is positive.
+
+### Total and delivered impulse
+
+```text
+I_total = integral T(t) dt
+
+I_delivered(t)
+  = integral from 0 to clamp(t, 0, burn_end) of T(tau) d tau
+```
+
+For a linear segment, area is a trapezoid:
+
+```text
+segment impulse
+  = 0.5 (T_left + T_right) delta_t
+```
+
+The default areas are:
+
+| interval (s) | impulse (N*s) |
+| --- | ---: |
+| 0.00–0.05 | 1.00 |
+| 0.05–0.12 | 1.82 |
+| 0.12–0.35 | 5.06 |
+| 0.35–0.70 | 6.30 |
+| 0.70–0.95 | 3.00 |
+| 0.95–1.05 | 0.40 |
+
+Therefore:
+
+```text
+burn duration  = 1.05 s
+total impulse  = 17.58 N*s
+peak thrust    = 28 N
+average thrust = 17.58 / 1.05
+               = 16.742857... N
+```
+
+Average thrust is area divided by duration, not generally the arithmetic mean of all sample values. Piecewise-linear interpolation cannot exceed its endpoints, so `28 N` is the exact peak of this stored polyline. Sparse samples could still miss a real motor's true peak.
+
+### Impulse and momentum
+
+The general vector relation is:
+
+```text
+J_net = integral F_net dt = delta_p
+```
+
+For RocketSim's constant mass:
+
+```text
+m delta_v = J_thrust + J_gravity + J_drag
+```
+
+Only when gravity and drag are removed does the isolated thrust result become:
+
+```text
+delta_v = (I_total / m) u_T
+```
+
+RocketSim integrates motor impulse exactly for its stored piecewise-linear curve on every completed internal segment. The trajectory is still a fixed-timestep approximation: position is semi-implicit, drag is evaluated from segment-start velocity, and impact is interpolated from the discrete path.
+
+### Read the motor timeline
+
+The horizontal axis is motor time; the vertical axis is thrust in newtons. Orange line segments and yellow points are the exact configured polyline. A nonzero final stored sample is shown as an open left-limit point plus a filled zero-thrust point at exact burnout. The default curve already ends at zero, so its endpoint is a single filled point. The green cursor follows simulation time during the burn. In coast it is clamped at the burn endpoint and explicitly labeled “clamped at burnout”; the Inspector continues showing actual flight time. The magenta marker identifies burn end.
+
+The timeline uses the same production curve as physics. It does not keep a second graph-only curve.
+
+In READY, the plot shows the configured motor but current thrust remains inactive at `0 N`. After launch at `t=0`, the active default thrust is `12 N`.
+
+The Inspector distinguishes:
+
+```text
+Current thrust        T(t), N
+Motor phase           READY / ACTIVE / COMPLETE
+Burn-time progress    elapsed burn-time fraction
+Delivered impulse     curve area delivered so far, N*s
+Total impulse         complete curve area, N*s
+Peak stored / average thrust N
+```
+
+Burn-time progress and delivered-impulse fraction are not the same for a nonuniform curve.
+
+### Guided motor experiment
+
+#### Predict
+
+Before launching, write answers:
+
+1. At which plotted sample is thrust largest?
+2. Must acceleration be largest at that same time?
+3. What does area under the curve represent?
+4. What happens to thrust, impulse, and velocity at burnout?
+
+#### Observe
+
+1. Launch with `SPACE`.
+2. Use the highest plotted sample and the stored-peak readout to identify the early `0.05 s` peak; do not try to catch it manually.
+3. Pause anywhere in the broad declining-thrust interval and record the actual displayed time.
+4. Record current thrust, delivered impulse, velocity, drag, net force, and acceleration.
+5. Press `RIGHT` repeatedly. Confirm that time, cursor, current thrust, delivered impulse, force arrows, acceleration, and velocity update while the simulation remains paused.
+6. Step through `1.05 s` burnout.
+7. Resume into coast. Confirm current thrust stays zero, total impulse stays `17.58 N*s`, and the labeled motor cursor remains at burn end while actual flight time continues.
+
+#### Explain
+
+Connect the chain:
+
+```text
+thrust curve
+→ motor impulse
+→ momentum change
+→ velocity
+→ quadratic drag
+→ trajectory
+```
+
+Thrust timing influences velocity timing. Because drag scales with speed squared, two equal-impulse curves can produce different drag histories and trajectories.
+
+### Zero-at-ignition laboratory example
+
+Instantaneous zero thrust does not imply zero impulse over every finite interval. The original proposed curve starts at `0 N` and reaches `28 N` at `0.05 s`. It cannot be the ground default because RocketSim has no pad support and its first free-flight step would move below ground. Use it above ground with gravity disabled:
+
+```bash
+conda run --no-capture-output -n rocketsim python - <<'PY'
+from rocket_sim import Simulation, SimulationConfig, ThrustCurve, ThrustSample, Vector2
+
+curve = ThrustCurve(
+    ThrustSample(t, thrust)
+    for t, thrust in (
+        (0.00, 0),
+        (0.05, 28),
+        (0.12, 24),
+        (0.35, 20),
+        (0.70, 16),
+        (0.95, 8),
+        (1.05, 0),
+    )
+)
+simulation = Simulation(
+    SimulationConfig(
+        thrust_curve=curve,
+        gravity_m_s2=0.0,
+        air_density_kg_m3=0.0,
+        initial_position_m=Vector2(0.0, 10.0),
+    )
+)
+simulation.launch()
+for _ in range(110):
+    simulation.step()
+
+print("T(0):", curve.thrust_at(0.0), "N")
+print("Impulse over first 0.01 s:", curve.impulse_between_ns(0.0, 0.01), "N*s")
+print("Total impulse:", curve.total_impulse_ns, "N*s")
+print("Final vertical velocity:", simulation.state.velocity_m_s.y, "m/s")
+PY
+```
+
+Predict the four printed values before running. The independent expectations are:
+
+```text
+T(0)                         0 N
+impulse over first 0.01 s    0.028 N*s
+total impulse                17.28 N*s
+final vertical velocity      17.28 m/s
+```
+
+The last equality uses `m=1 kg`, constant mass, vertical thrust, zero gravity, and zero drag. It is not a general statement for an actual flight.
+
+### Check your understanding
+
+1. Why are newtons and newton-seconds different quantities?
+2. Why is average thrust not generally the mean of all listed thrust samples?
+3. Can two motors have the same peak thrust but different total impulse?
+4. With gravity and drag removed, what does equal total impulse imply for equal constant masses and directions?
+5. Why can equal-impulse curves produce different trajectories when drag is active?
+6. How can `T(0)=0` coexist with positive impulse over the next interval?
+7. Which Prompt 04 quantities are exact for the stored curve, and which flight quantities remain numerical approximations?
+8. Why does current RocketSim keep mass constant even though real motors consume propellant?
+
+---
+
+# Looking ahead without claiming implementation
+
+Later approved milestones may add one validated effect at a time. If variable mass is added, Lessons 3, 4, 5, 8, and 9 must be revisited. If atmosphere changes with altitude, Lessons 6 and 7 must change. Wind would revise air-relative velocity. Rotation and stability would revise vectors, powered flight, drag, and the meaning of the rocket drawing.
+
+Those features are not implemented now. The course evolves retroactively so older explanations never remain silently obsolete.
diff --git a/docs/product/PROJECT_UNDERSTANDING.md b/docs/product/PROJECT_UNDERSTANDING.md
index 929b2a1..e31b21f 100644
--- a/docs/product/PROJECT_UNDERSTANDING.md
+++ b/docs/product/PROJECT_UNDERSTANDING.md
@@ -5 +5 @@
-RocketSim is a trustworthy, understandable 2D model-rocket learning simulator rather than an engineering-grade launch predictor. Prompt 03 completes the constant-property quadratic-drag milestone and adds an educational Physics Inspector without adding another physical model.
+RocketSim is a scientifically validated, interactive rocketry-learning simulator whose educational course evolves with the implemented model. It remains a trustworthy, understandable 2D learning model rather than an engineering-grade launch predictor. Prompt 04 adds piecewise-linear sampled thrust and motor impulse while establishing the permanent Living Rocketry Course.
@@ -14 +14 @@ The forces are:
-- constant thrust `T(cos(theta), sin(theta))` during `0 <= t < burn_time`; and
+- time-varying sampled thrust `T(t)(cos(theta), sin(theta))` during the curve's half-open burn interval; and
@@ -18,0 +19,2 @@ Air is stationary, so rocket velocity relative to air is numerically equal to gr
+One immutable `ThrustCurve` is the propulsion source of truth. Its final sample defines burn duration; its exact polyline area defines total and delivered impulse. The default curve is self-authored synthetic data with `1.05 s` duration, `17.58 N*s` total impulse, `28 N` peak thrust, and `16.742857... N` average thrust. It is not measured or certified motor data. The rocket mass and thrust direction remain constant.
+
@@ -22,0 +25 @@ src/rocket_sim/config.py       immutable Vector2 and validated run constants
+src/rocket_sim/propulsion.py   sampled curve, interpolation, and impulse metrics
@@ -24,2 +27,2 @@ src/rocket_sim/physics.py      thrust, gravity, drag, force breakdown, and Euler
-src/rocket_sim/simulation.py   state, lifecycle, fixed-step clock, events, and history
-src/rocket_sim/rendering.py    world transform, force arrows, and Physics Inspector
+src/rocket_sim/simulation.py   lifecycle, fixed outer clock, knot segments, and history
+src/rocket_sim/rendering.py    force arrows, Inspector, and motor timeline
@@ -34,2 +37,2 @@ The physics modules do not import Pygame. Rendering consumes `Simulation.current
-- Every numerical segment evaluates thrust, gravity, and drag from its starting time and velocity.
-- Semi-implicit Euler then updates velocity before position.
+- Every fixed outer step is split at all crossed thrust knots.
+- Every internal segment integrates represented thrust impulse exactly, applies constant gravity and drag from segment-start velocity, then updates velocity before position.
@@ -38,0 +42 @@ The physics modules do not import Pygame. Rendering consumes `Simulation.current
+- Curve knots are part of the active-drag numerical mesh; exact motor impulse does not imply an exact trajectory.
@@ -45 +49 @@ The physics modules do not import Pygame. Rendering consumes `Simulation.current
-The Pygame application shows powered and coast trajectory segments, current phase and burnout status, thrust/gravity/drag/net-force arrows, numerical force components and magnitudes, aerodynamic parameters, and the implemented equations. READY explicitly reports forces as inactive alongside zero stored acceleration; it does not invent a pad normal force.
+The Pygame application shows powered and coast trajectory segments, current phase and burnout status, thrust/gravity/drag/net-force arrows, numerical force components and magnitudes, motor/aerodynamic parameters, and the implemented equations. A motor timeline plots production samples, current motor cursor, peak, and burnout. READY explicitly reports forces as inactive alongside zero stored acceleration; it does not invent a pad normal force.
@@ -51 +55 @@ Controls are SPACE launch/pause/resume, RIGHT single-step while paused, R reset,
-The suite preserves Prompt 02 with explicitly disabled drag and adds independent vector-force oracles, all quadrants, exact zero cases, `v^2` scaling, terminal velocity, a closed-form vertical quadratic-drag fall, measured first-order timestep convergence, active-drag burnout, active-drag reset and FPS independence, paused stepping, rendering isolation, Inspector sourcing, and a bounded SDL dummy application smoke test.
+The suite preserves Prompts 02–03 through constant/zero curves and adds independent sample validation, interpolation, impulse, default metrics, knot segmentation, burn-end, impulse–momentum, active-drag force, independent-RK4 convergence, sampled-thrust reset/FPS, paused stepping, rendering isolation, Inspector/timeline sourcing, and bounded SDL smoke evidence.
@@ -55 +59 @@ The suite preserves Prompt 02 with explicitly disabled drag and adds independent
-Density, `Cd`, and effective reference area are constant and direction-independent. There is no wind, altitude-varying atmosphere, lift, compressibility, Mach/Reynolds dependence, variable mass, real motor curve, recovery, collision dynamics, rotation, stability, guidance, control, plotting, experiment export, calibration, or uncertainty model. Semi-implicit Euler is explicit with respect to drag and can become unstable for sufficiently large timestep or speed; no artificial clamp conceals that limitation.
+Density, `Cd`, and effective reference area are constant and direction-independent. There is no wind, altitude-varying atmosphere, lift, compressibility, Mach/Reynolds dependence, variable mass, propellant depletion, measured motor import, pad/rail contact, recovery, collision dynamics, rotation, stability, guidance, control, plotting, experiment export, calibration, or uncertainty model. Semi-implicit Euler is explicit with respect to drag and can become unstable for sufficiently large timestep or speed; no artificial clamp conceals that limitation.
@@ -57 +61 @@ Density, `Cd`, and effective reference area are constant and direction-independe
-The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction. Prompt 04 has not begun.
+The point-mass result is not equivalent to 3D flight dynamics and is not an engineering or safety prediction. Prompt 05 has not begun.
diff --git a/src/rocket_sim/__init__.py b/src/rocket_sim/__init__.py
index c9f1d0f..414993c 100644
--- a/src/rocket_sim/__init__.py
+++ b/src/rocket_sim/__init__.py
@@ -4,0 +5,5 @@ from .physics import ForceBreakdown
+from .propulsion import (
+    DEFAULT_EDUCATIONAL_THRUST_CURVE,
+    ThrustCurve,
+    ThrustSample,
+)
@@ -11,0 +17 @@ __all__ = [
+    "DEFAULT_EDUCATIONAL_THRUST_CURVE",
@@ -14,0 +21,2 @@ __all__ = [
+    "ThrustCurve",
+    "ThrustSample",
diff --git a/src/rocket_sim/app.py b/src/rocket_sim/app.py
index 7ab9b54..4c777e4 100644
--- a/src/rocket_sim/app.py
+++ b/src/rocket_sim/app.py
@@ -44 +44 @@ def run(max_frames: int | None = None) -> int:
-        pygame.display.set_caption("RocketSim - quadratic-drag Physics Inspector")
+        pygame.display.set_caption("RocketSim - sampled-thrust flight laboratory")
diff --git a/src/rocket_sim/config.py b/src/rocket_sim/config.py
index e8e38fa..9bd0e12 100644
--- a/src/rocket_sim/config.py
+++ b/src/rocket_sim/config.py
@@ -7,0 +8,2 @@ import math
+from .propulsion import DEFAULT_EDUCATIONAL_THRUST_CURVE, ThrustCurve
+
@@ -44 +46 @@ class SimulationConfig:
-    """Physical parameters for one deterministic Milestone 2 run."""
+    """Physical parameters for one deterministic sampled-thrust run."""
@@ -47,2 +49,3 @@ class SimulationConfig:
-    thrust_n: float = 20.0
-    burn_time_s: float = 1.0
+    thrust_curve: ThrustCurve = field(
+        default_factory=lambda: DEFAULT_EDUCATIONAL_THRUST_CURVE
+    )
@@ -61,2 +63,0 @@ class SimulationConfig:
-            "thrust_n": self.thrust_n,
-            "burn_time_s": self.burn_time_s,
@@ -77,4 +78,2 @@ class SimulationConfig:
-        if self.thrust_n < 0.0:
-            raise ValueError("thrust_n must be non-negative")
-        if self.burn_time_s < 0.0:
-            raise ValueError("burn_time_s must be non-negative")
+        if not isinstance(self.thrust_curve, ThrustCurve):
+            raise TypeError("thrust_curve must be a ThrustCurve")
diff --git a/src/rocket_sim/physics.py b/src/rocket_sim/physics.py
index 6dbd35e..aa020c1 100644
--- a/src/rocket_sim/physics.py
+++ b/src/rocket_sim/physics.py
@@ -33 +33 @@ def thrust_force_n(config: SimulationConfig, time_s: float) -> Vector2:
-    """Return constant world-angle thrust on the half-open burn interval."""
+    """Return instantaneous sampled thrust at the fixed world angle."""
@@ -37,2 +37 @@ def thrust_force_n(config: SimulationConfig, time_s: float) -> Vector2:
-    if not 0.0 <= time_s < config.burn_time_s:
-        return Vector2(0.0, 0.0)
+    thrust_n = config.thrust_curve.thrust_at(time_s)
@@ -40,2 +39,14 @@ def thrust_force_n(config: SimulationConfig, time_s: float) -> Vector2:
-        config.thrust_n * math.cos(config.launch_angle_rad),
-        config.thrust_n * math.sin(config.launch_angle_rad),
+        thrust_n * math.cos(config.launch_angle_rad),
+        thrust_n * math.sin(config.launch_angle_rad),
+    )
+
+
+def thrust_impulse_n_s(
+    config: SimulationConfig, start_time_s: float, end_time_s: float
+) -> Vector2:
+    """Return exact motor impulse over an interval at the fixed direction."""
+
+    impulse_ns = config.thrust_curve.impulse_between_ns(start_time_s, end_time_s)
+    return Vector2(
+        impulse_ns * math.cos(config.launch_angle_rad),
+        impulse_ns * math.sin(config.launch_angle_rad),
@@ -110,0 +122,20 @@ def semi_implicit_euler(
+
+
+def semi_implicit_impulse_step(
+    position_m: Vector2,
+    velocity_m_s: Vector2,
+    thrust_impulse_ns: Vector2,
+    other_force_n: Vector2,
+    mass_kg: float,
+    duration_s: float,
+) -> tuple[Vector2, Vector2]:
+    """Advance using exact thrust impulse and start-state non-thrust force."""
+
+    if not math.isfinite(mass_kg) or mass_kg <= 0.0:
+        raise ValueError("mass_kg must be finite and greater than zero")
+    if not math.isfinite(duration_s) or duration_s <= 0.0:
+        raise ValueError("duration_s must be finite and greater than zero")
+    total_impulse_ns = thrust_impulse_ns + other_force_n * duration_s
+    new_velocity = velocity_m_s + total_impulse_ns * (1.0 / mass_kg)
+    new_position = position_m + new_velocity * duration_s
+    return new_position, new_velocity
diff --git a/src/rocket_sim/propulsion.py b/src/rocket_sim/propulsion.py
new file mode 100644
index 0000000..1eeb15a
--- /dev/null
+++ b/src/rocket_sim/propulsion.py
@@ -0,0 +1,193 @@
+"""Immutable sampled thrust curves and exact piecewise-linear impulse metrics."""
+
+from __future__ import annotations
+
+from bisect import bisect_right
+from dataclasses import dataclass
+from typing import Iterable
+import math
+
+
+@dataclass(frozen=True, slots=True)
+class ThrustSample:
+    """One thrust-curve knot in SI units."""
+
+    time_s: float
+    thrust_n: float
+
+    def __post_init__(self) -> None:
+        if not math.isfinite(self.time_s):
+            raise ValueError("thrust sample time_s must be finite")
+        if not math.isfinite(self.thrust_n):
+            raise ValueError("thrust sample thrust_n must be finite")
+        if self.time_s < 0.0:
+            raise ValueError("thrust sample time_s must be non-negative")
+        if self.thrust_n < 0.0:
+            raise ValueError("thrust sample thrust_n must be non-negative")
+
+
+@dataclass(frozen=True, slots=True, init=False)
+class ThrustCurve:
+    """Validated piecewise-linear thrust with a half-open burn interval."""
+
+    samples: tuple[ThrustSample, ...]
+    _sample_times_s: tuple[float, ...]
+    _prefix_impulse_ns: tuple[float, ...]
+
+    def __init__(self, samples: Iterable[ThrustSample]) -> None:
+        owned_samples = tuple(samples)
+        if not owned_samples:
+            raise ValueError("a thrust curve requires at least one sample")
+        if any(not isinstance(sample, ThrustSample) for sample in owned_samples):
+            raise TypeError("thrust curve samples must be ThrustSample values")
+        if owned_samples[0].time_s != 0.0:
+            raise ValueError("the first thrust sample time must be exactly zero")
+        for before, after in zip(owned_samples, owned_samples[1:], strict=False):
+            if after.time_s <= before.time_s:
+                raise ValueError("thrust sample times must be strictly increasing")
+        if len(owned_samples) == 1 and owned_samples[0].thrust_n != 0.0:
+            raise ValueError("a zero-duration curve must contain only zero thrust")
+
+        prefix_impulse = [0.0]
+        for before, after in zip(owned_samples, owned_samples[1:], strict=False):
+            prefix_impulse.append(
+                prefix_impulse[-1]
+                + 0.5
+                * (before.thrust_n + after.thrust_n)
+                * (after.time_s - before.time_s)
+            )
+
+        object.__setattr__(self, "samples", owned_samples)
+        object.__setattr__(
+            self, "_sample_times_s", tuple(sample.time_s for sample in owned_samples)
+        )
+        object.__setattr__(self, "_prefix_impulse_ns", tuple(prefix_impulse))
+
+    @classmethod
+    def zero(cls) -> ThrustCurve:
+        """Return the zero-duration, zero-thrust limiting curve."""
+
+        return cls((ThrustSample(0.0, 0.0),))
+
+    @classmethod
+    def constant(cls, thrust_n: float, burn_duration_s: float) -> ThrustCurve:
+        """Return constant thrust over ``0 <= t < burn_duration_s``."""
+
+        if not math.isfinite(thrust_n) or thrust_n < 0.0:
+            raise ValueError("constant thrust_n must be finite and non-negative")
+        if not math.isfinite(burn_duration_s) or burn_duration_s < 0.0:
+            raise ValueError(
+                "constant burn_duration_s must be finite and non-negative"
+            )
+        if burn_duration_s == 0.0:
+            if thrust_n != 0.0:
+                raise ValueError("positive thrust requires a positive burn duration")
+            return cls.zero()
+        return cls(
+            (
+                ThrustSample(0.0, thrust_n),
+                ThrustSample(burn_duration_s, thrust_n),
+            )
+        )
+
+    @property
+    def burn_duration_s(self) -> float:
+        return self.samples[-1].time_s
+
+    @property
+    def total_impulse_ns(self) -> float:
+        return self._prefix_impulse_ns[-1]
+
+    @property
+    def average_thrust_n(self) -> float:
+        if self.burn_duration_s == 0.0:
+            return 0.0
+        return self.total_impulse_ns / self.burn_duration_s
+
+    @property
+    def peak_thrust_n(self) -> float:
+        """Return the maximum stored ordinate, the curve's thrust supremum."""
+
+        return max(sample.thrust_n for sample in self.samples)
+
+    def thrust_at(self, time_s: float) -> float:
+        """Return instantaneous thrust, zero outside the half-open burn."""
+
+        self._validate_query_time(time_s)
+        if time_s < 0.0 or time_s >= self.burn_duration_s:
+            return 0.0
+
+        left_index = bisect_right(self._sample_times_s, time_s) - 1
+        left = self.samples[left_index]
+        right = self.samples[left_index + 1]
+        fraction = (time_s - left.time_s) / (right.time_s - left.time_s)
+        return left.thrust_n + fraction * (right.thrust_n - left.thrust_n)
+
+    def delivered_impulse_ns(self, time_s: float) -> float:
+        """Return exact curve impulse delivered through the clamped time."""
+
+        self._validate_query_time(time_s)
+        if time_s <= 0.0 or self.burn_duration_s == 0.0:
+            return 0.0
+        if time_s >= self.burn_duration_s:
+            return self.total_impulse_ns
+
+        left_index = bisect_right(self._sample_times_s, time_s) - 1
+        left = self.samples[left_index]
+        right = self.samples[left_index + 1]
+        duration_s = time_s - left.time_s
+        slope_n_s = (right.thrust_n - left.thrust_n) / (
+            right.time_s - left.time_s
+        )
+        partial_impulse_ns = (
+            left.thrust_n * duration_s
+            + 0.5 * slope_n_s * duration_s * duration_s
+        )
+        return self._prefix_impulse_ns[left_index] + partial_impulse_ns
+
+    def impulse_between_ns(self, start_time_s: float, end_time_s: float) -> float:
+        """Return exact curve impulse over an ordered time interval."""
+
+        self._validate_query_time(start_time_s)
+        self._validate_query_time(end_time_s)
+        if end_time_s < start_time_s:
+            raise ValueError("impulse interval end must not precede its start")
+        return self.delivered_impulse_ns(
+            end_time_s
+        ) - self.delivered_impulse_ns(start_time_s)
+
+    def knots_strictly_between(
+        self, start_time_s: float, end_time_s: float
+    ) -> tuple[float, ...]:
+        """Return configured knot times strictly inside an ordered interval."""
+
+        self._validate_query_time(start_time_s)
+        self._validate_query_time(end_time_s)
+        if end_time_s < start_time_s:
+            raise ValueError("knot interval end must not precede its start")
+        return tuple(
+            time_s
+            for time_s in self._sample_times_s
+            if start_time_s < time_s < end_time_s
+        )
+
+    @staticmethod
+    def _validate_query_time(time_s: float) -> None:
+        if not math.isfinite(time_s):
+            raise ValueError("thrust-curve query time must be finite")
+
+
+# Self-authored educational data, not measurements from a certified motor.
+# The nonzero ignition value keeps the default ground launch admissible without
+# adding pad, rail, or support-force physics.
+DEFAULT_EDUCATIONAL_THRUST_CURVE = ThrustCurve(
+    (
+        ThrustSample(0.00, 12.0),
+        ThrustSample(0.05, 28.0),
+        ThrustSample(0.12, 24.0),
+        ThrustSample(0.35, 20.0),
+        ThrustSample(0.70, 16.0),
+        ThrustSample(0.95, 8.0),
+        ThrustSample(1.05, 0.0),
+    )
+)
diff --git a/src/rocket_sim/rendering.py b/src/rocket_sim/rendering.py
index ec4f67e..550d317 100644
--- a/src/rocket_sim/rendering.py
+++ b/src/rocket_sim/rendering.py
@@ -11,0 +12 @@ from .physics import ForceBreakdown
+from .propulsion import ThrustCurve
@@ -27,0 +29,55 @@ CONTROL_ROWS = (
+@dataclass(frozen=True, slots=True)
+class ThrustTimelineGeometry:
+    """Rendering-only coordinates derived from one production thrust curve."""
+
+    sample_points_px: tuple[tuple[int, int], ...]
+    cursor_x_px: int
+    burnout_x_px: int
+    current_thrust_n: float
+    cursor_time_s: float
+    burnout_zero_point_px: tuple[int, int]
+    terminal_sample_is_left_limit: bool
+
+
+def thrust_timeline_geometry(
+    thrust_curve: ThrustCurve,
+    current_time_s: float,
+    current_thrust_n: float,
+    graph_rect: pygame.Rect,
+) -> ThrustTimelineGeometry:
+    """Map production samples and current motor time into a graph rectangle."""
+
+    burn_duration_s = thrust_curve.burn_duration_s
+    peak_thrust_n = thrust_curve.peak_thrust_n
+    cursor_time_s = min(max(current_time_s, 0.0), burn_duration_s)
+
+    def time_x(time_s: float) -> int:
+        if burn_duration_s == 0.0:
+            return graph_rect.left
+        return round(
+            graph_rect.left + graph_rect.width * time_s / burn_duration_s
+        )
+
+    def thrust_y(thrust_n: float) -> int:
+        if peak_thrust_n == 0.0:
+            return graph_rect.bottom
+        return round(
+            graph_rect.bottom - graph_rect.height * thrust_n / peak_thrust_n
+        )
+
+    return ThrustTimelineGeometry(
+        sample_points_px=tuple(
+            (time_x(sample.time_s), thrust_y(sample.thrust_n))
+            for sample in thrust_curve.samples
+        ),
+        cursor_x_px=time_x(cursor_time_s),
+        burnout_x_px=time_x(burn_duration_s),
+        current_thrust_n=current_thrust_n,
+        cursor_time_s=cursor_time_s,
+        burnout_zero_point_px=(time_x(burn_duration_s), thrust_y(0.0)),
+        terminal_sample_is_left_limit=(
+            burn_duration_s > 0.0 and thrust_curve.samples[-1].thrust_n > 0.0
+        ),
+    )
+
+
@@ -73,4 +129,30 @@ def physics_inspector_rows(
-    if state.phase is FlightPhase.READY:
-        burnout = f"pending at {simulation.config.burn_time_s:.3f} s"
-    elif state.time_s >= simulation.config.burn_time_s:
-        burnout = f"complete at {simulation.config.burn_time_s:.3f} s"
+    thrust_curve = simulation.config.thrust_curve
+    if thrust_curve.burn_duration_s == 0.0:
+        burnout = "zero-duration curve (no burn)"
+        motor_phase = (
+            "READY / NO BURN"
+            if state.phase is FlightPhase.READY
+            else "COMPLETE / NO BURN"
+        )
+    elif state.phase is FlightPhase.READY:
+        burnout = (
+            f"pending at {thrust_curve.burn_duration_s:.3f} s"
+        )
+        motor_phase = "READY"
+    elif state.time_s >= thrust_curve.burn_duration_s:
+        burnout = (
+            f"complete at {thrust_curve.burn_duration_s:.3f} s"
+        )
+        motor_phase = "COMPLETE"
+    else:
+        burnout = (
+            f"pending at {thrust_curve.burn_duration_s:.3f} s"
+        )
+        motor_phase = (
+            "ACTIVE (flight terminal)"
+            if state.phase is FlightPhase.LANDED
+            else "ACTIVE"
+        )
+
+    if thrust_curve.burn_duration_s == 0.0:
+        burn_progress = "N/A (zero-duration)"
@@ -78 +160,4 @@ def physics_inspector_rows(
-        burnout = f"pending at {simulation.config.burn_time_s:.3f} s"
+        fraction = min(
+            max(state.time_s / thrust_curve.burn_duration_s, 0.0), 1.0
+        )
+        burn_progress = f"{100.0 * fraction:6.2f}%"
@@ -101,0 +187,10 @@ def physics_inspector_rows(
+        "MOTOR",
+        f"Motor phase: {motor_phase}",
+        f"Current thrust: {forces.thrust_n.magnitude:7.3f} N",
+        f"Burn-time progress: {burn_progress}",
+        f"Burn duration: {thrust_curve.burn_duration_s:7.3f} s",
+        f"Peak stored thrust: {thrust_curve.peak_thrust_n:7.3f} N",
+        f"Average thrust: {thrust_curve.average_thrust_n:7.3f} N",
+        f"Delivered impulse: {simulation.delivered_impulse_ns:7.3f} N*s",
+        f"Total impulse: {thrust_curve.total_impulse_ns:7.3f} N*s",
+        "",
@@ -115 +210 @@ def physics_inspector_rows(
-        "Ft = T(cos(theta), sin(theta))",
+        "Ft(t) = T(t) (cos(theta), sin(theta))",
@@ -118,0 +214 @@ def physics_inspector_rows(
+        "I = integral T(t) dt",
@@ -179,0 +276,4 @@ class Renderer:
+        forces = simulation.current_forces
+        self._draw_thrust_timeline(
+            surface, simulation, forces.thrust_n.magnitude
+        )
@@ -187 +286,0 @@ class Renderer:
-        forces = simulation.current_forces
@@ -317,0 +417,91 @@ class Renderer:
+    def _draw_thrust_timeline(
+        self,
+        surface: pygame.Surface,
+        simulation: Simulation,
+        current_thrust_n: float,
+    ) -> None:
+        panel = pygame.Rect(self.world_width_px - 374, 82, 352, 184)
+        graph = pygame.Rect(panel.left + 42, panel.top + 30, 290, 118)
+        curve = simulation.config.thrust_curve
+        geometry = thrust_timeline_geometry(
+            curve, simulation.state.time_s, current_thrust_n, graph
+        )
+
+        pygame.draw.rect(surface, (18, 31, 53), panel, border_radius=6)
+        pygame.draw.rect(surface, (78, 98, 126), panel, 1, border_radius=6)
+        pygame.draw.line(
+            surface,
+            (145, 159, 181),
+            (graph.left, graph.bottom),
+            (graph.right, graph.bottom),
+            1,
+        )
+        pygame.draw.line(
+            surface,
+            (145, 159, 181),
+            (graph.left, graph.top),
+            (graph.left, graph.bottom),
+            1,
+        )
+
+        pygame.draw.line(
+            surface,
+            (238, 112, 214),
+            (geometry.burnout_x_px, graph.top),
+            (geometry.burnout_x_px, graph.bottom),
+            1,
+        )
+
+        if len(geometry.sample_points_px) > 1:
+            pygame.draw.lines(
+                surface,
+                (255, 174, 66),
+                False,
+                geometry.sample_points_px,
+                2,
+            )
+        filled_points = geometry.sample_points_px
+        if geometry.terminal_sample_is_left_limit:
+            filled_points = geometry.sample_points_px[:-1]
+        for point in filled_points:
+            pygame.draw.circle(surface, (245, 214, 96), point, 3)
+        if geometry.terminal_sample_is_left_limit:
+            terminal_point = geometry.sample_points_px[-1]
+            pygame.draw.circle(surface, (18, 31, 53), terminal_point, 4)
+            pygame.draw.circle(surface, (245, 214, 96), terminal_point, 4, 1)
+            pygame.draw.circle(
+                surface, (245, 214, 96), geometry.burnout_zero_point_px, 3
+            )
+        pygame.draw.line(
+            surface,
+            (102, 221, 154),
+            (geometry.cursor_x_px, graph.top),
+            (geometry.cursor_x_px, graph.bottom),
+            2,
+        )
+
+        heading = self._small_font.render(
+            "MOTOR THRUST TIMELINE", True, (245, 214, 96)
+        )
+        surface.blit(heading, (panel.left + 10, panel.top + 7))
+        labels = (
+            ("T (N)", (panel.left + 5, graph.top - 2)),
+            (
+                f"motor cursor {geometry.cursor_time_s:.3f} s"
+                + (
+                    " (clamped at burnout)"
+                    if simulation.state.time_s > curve.burn_duration_s
+                    else ""
+                ),
+                (panel.left + 10, graph.bottom + 7),
+            ),
+            (
+                f"T={geometry.current_thrust_n:.2f} N  stored peak={curve.peak_thrust_n:.2f} N",
+                (panel.left + 190, panel.top + 7),
+            ),
+            ("t (s)", (graph.right - 26, graph.bottom - 17)),
+        )
+        for label, position in labels:
+            rendered = self._small_font.render(label, True, (213, 222, 236))
+            surface.blit(rendered, position)
+
@@ -329 +519,6 @@ class Renderer:
-            elif text in {"FORCES", "PARAMETERS (constant)", "EQUATIONS"}:
+            elif text in {
+                "MOTOR",
+                "FORCES",
+                "PARAMETERS (constant)",
+                "EQUATIONS",
+            }:
@@ -333 +528 @@ class Renderer:
-            surface.blit(rendered, (panel_x, 16 + index * 23))
+            surface.blit(rendered, (panel_x, 12 + index * 17))
diff --git a/src/rocket_sim/simulation.py b/src/rocket_sim/simulation.py
index a156ef3..3b7ba99 100644
--- a/src/rocket_sim/simulation.py
+++ b/src/rocket_sim/simulation.py
@@ -12,0 +13 @@ from .physics import (
+    drag_force_n,
@@ -14 +15,3 @@ from .physics import (
-    semi_implicit_euler,
+    gravity_force_n,
+    semi_implicit_impulse_step,
+    thrust_impulse_n_s,
@@ -82,0 +86,4 @@ class Simulation:
+    @property
+    def delivered_impulse_ns(self) -> float:
+        return self.config.thrust_curve.delivered_impulse_ns(self._state.time_s)
+
@@ -117,4 +124,12 @@ class Simulation:
-            first_segment_s = self.config.physics_dt_s
-            if 0.0 < self.config.burn_time_s < first_segment_s:
-                first_segment_s = self.config.burn_time_s
-            trial_position, _ = semi_implicit_euler(
+            first_segment_s = min(
+                (
+                    *self.config.thrust_curve.knots_strictly_between(
+                        0.0, self.config.physics_dt_s
+                    ),
+                    self.config.physics_dt_s,
+                )
+            )
+            initial_other_force = gravity_force_n(
+                self.config.mass_kg, self.config.gravity_m_s2
+            ) + drag_force_n(self.config, self._state.velocity_m_s)
+            trial_position, _ = semi_implicit_impulse_step(
@@ -123 +138,3 @@ class Simulation:
-                initial_acceleration,
+                thrust_impulse_n_s(self.config, 0.0, first_segment_s),
+                initial_other_force,
+                self.config.mass_kg,
@@ -223 +240 @@ class Simulation:
-        if 0.0 <= time_s < self.config.burn_time_s:
+        if 0.0 <= time_s < self.config.thrust_curve.burn_duration_s:
@@ -230,8 +247,8 @@ class Simulation:
-        burnout_s = self.config.burn_time_s
-
-        if start_s < burnout_s < target_s:
-            self._advance_segment_to(burnout_s)
-            if not self.is_finished:
-                self._advance_segment_to(target_s)
-        else:
-            self._advance_segment_to(target_s)
+        boundaries = (
+            *self.config.thrust_curve.knots_strictly_between(start_s, target_s),
+            target_s,
+        )
+        for boundary_s in boundaries:
+            self._advance_segment_to(boundary_s)
+            if self.is_finished:
+                break
@@ -242,4 +259,4 @@ class Simulation:
-        acceleration = acceleration_m_s2(
-            self.config, previous.time_s, previous.velocity_m_s
-        )
-        trial_position, trial_velocity = semi_implicit_euler(
+        other_force = gravity_force_n(
+            self.config.mass_kg, self.config.gravity_m_s2
+        ) + drag_force_n(self.config, previous.velocity_m_s)
+        trial_position, trial_velocity = semi_implicit_impulse_step(
@@ -248 +265,3 @@ class Simulation:
-            acceleration,
+            thrust_impulse_n_s(self.config, previous.time_s, target_time_s),
+            other_force,
+            self.config.mass_kg,
diff --git a/tests/test_aerodynamics.py b/tests/test_aerodynamics.py
index 4e1ca64..812e6f8 100644
--- a/tests/test_aerodynamics.py
+++ b/tests/test_aerodynamics.py
@@ -5 +5 @@ import pytest
-from rocket_sim import SimulationConfig, Vector2
+from rocket_sim import SimulationConfig, ThrustCurve, Vector2
@@ -13 +13 @@ from rocket_sim.physics import (
-def _aerodynamic_config(**overrides: float) -> SimulationConfig:
+def _aerodynamic_config(**overrides: object) -> SimulationConfig:
@@ -16,2 +16 @@ def _aerodynamic_config(**overrides: float) -> SimulationConfig:
-        "thrust_n": 10.0,
-        "burn_time_s": 2.0,
+        "thrust_curve": ThrustCurve.constant(10.0, 2.0),
@@ -25 +24 @@ def _aerodynamic_config(**overrides: float) -> SimulationConfig:
-    return SimulationConfig(**values)
+    return SimulationConfig(**values)  # type: ignore[arg-type]
@@ -109,2 +108 @@ def test_terminal_velocity_is_force_equilibrium_with_restoring_signs() -> None:
-        thrust_n=0.0,
-        burn_time_s=0.0,
+        thrust_curve=ThrustCurve.zero(),
diff --git a/tests/test_analytical_validation.py b/tests/test_analytical_validation.py
index 112ac7e..ddad314 100644
--- a/tests/test_analytical_validation.py
+++ b/tests/test_analytical_validation.py
@@ -5 +5,7 @@ import pytest
-from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
+from rocket_sim import (
+    FlightPhase,
+    Simulation,
+    SimulationConfig,
+    ThrustCurve,
+    Vector2,
+)
@@ -18,2 +24 @@ def test_gravity_only_matches_independent_projectile_reference() -> None:
-        thrust_n=0.0,
-        burn_time_s=0.0,
+        thrust_curve=ThrustCurve.zero(),
@@ -51,2 +56 @@ def test_powered_motion_matches_independent_constant_acceleration_reference() ->
-        thrust_n=thrust,
-        burn_time_s=2.0,
+        thrust_curve=ThrustCurve.constant(thrust, 2.0),
@@ -82 +86,5 @@ def test_piecewise_powered_and_coast_motion_matches_closed_form_error() -> None:
-    config = SimulationConfig(physics_dt_s=dt, air_density_kg_m3=0.0)
+    config = SimulationConfig(
+        thrust_curve=ThrustCurve.constant(20.0, 1.0),
+        physics_dt_s=dt,
+        air_density_kg_m3=0.0,
+    )
@@ -111,0 +120,6 @@ def test_default_vertical_launch_has_negligible_horizontal_motion() -> None:
+    half_second = min(
+        simulation.trajectory, key=lambda state: abs(state.time_s - 0.5)
+    )
+    one_second = min(
+        simulation.trajectory, key=lambda state: abs(state.time_s - 1.0)
+    )
@@ -114,2 +128,2 @@ def test_default_vertical_launch_has_negligible_horizontal_motion() -> None:
-    assert simulation.trajectory[50].velocity_m_s.y > 0.0
-    assert simulation.state.velocity_m_s.y < simulation.trajectory[100].velocity_m_s.y
+    assert half_second.velocity_m_s.y > 0.0
+    assert simulation.state.velocity_m_s.y < one_second.velocity_m_s.y
@@ -121,2 +135 @@ def test_zero_gravity_powered_then_coast_limit() -> None:
-        thrust_n=8.0,
-        burn_time_s=0.5,
+        thrust_curve=ThrustCurve.constant(8.0, 0.5),
@@ -139,2 +152 @@ def test_zero_force_preserves_uniform_motion() -> None:
-        thrust_n=0.0,
-        burn_time_s=0.0,
+        thrust_curve=ThrustCurve.zero(),
diff --git a/tests/test_config.py b/tests/test_config.py
index d1fe59b..62d3975 100644
--- a/tests/test_config.py
+++ b/tests/test_config.py
@@ -5 +5 @@ import pytest
-from rocket_sim import SimulationConfig, Vector2
+from rocket_sim import SimulationConfig, ThrustCurve, Vector2
@@ -10,2 +10 @@ def test_zero_valued_limiting_parameters_are_valid() -> None:
-        thrust_n=0.0,
-        burn_time_s=0.0,
+        thrust_curve=ThrustCurve.zero(),
@@ -18,2 +17 @@ def test_zero_valued_limiting_parameters_are_valid() -> None:
-    assert config.thrust_n == 0.0
-    assert config.burn_time_s == 0.0
+    assert config.thrust_curve == ThrustCurve.zero()
@@ -41,2 +38,0 @@ def test_default_aerodynamic_values_are_documented_educational_constants() -> No
-        ("thrust_n", -1.0),
-        ("burn_time_s", -1.0),
@@ -60,2 +55,0 @@ def test_invalid_physical_ranges_are_rejected(field: str, value: float) -> None:
-        "thrust_n",
-        "burn_time_s",
@@ -84,0 +79,10 @@ def test_initial_altitude_below_ground_is_rejected() -> None:
+
+
+def test_thrust_curve_is_the_only_propulsion_configuration_field() -> None:
+    field_names = set(SimulationConfig.__dataclass_fields__)
+
+    assert "thrust_curve" in field_names
+    assert "thrust_n" not in field_names
+    assert "burn_time_s" not in field_names
+    with pytest.raises(TypeError, match="thrust_curve"):
+        SimulationConfig(thrust_curve=object())  # type: ignore[arg-type]
diff --git a/tests/test_convergence.py b/tests/test_convergence.py
index dfed43d..ecc7eaa 100644
--- a/tests/test_convergence.py
+++ b/tests/test_convergence.py
@@ -5 +5 @@ import pytest
-from rocket_sim import Simulation, SimulationConfig, Vector2
+from rocket_sim import Simulation, SimulationConfig, ThrustCurve, Vector2
@@ -13,2 +13 @@ def _powered_position_error(dt: float) -> float:
-            thrust_n=12.0,
-            burn_time_s=2.0,
+            thrust_curve=ThrustCurve.constant(12.0, 2.0),
@@ -40 +39,5 @@ def _default_landing_time_error(dt: float, analytical_time_s: float) -> float:
-        SimulationConfig(physics_dt_s=dt, air_density_kg_m3=0.0)
+        SimulationConfig(
+            thrust_curve=ThrustCurve.constant(20.0, 1.0),
+            physics_dt_s=dt,
+            air_density_kg_m3=0.0,
+        )
diff --git a/tests/test_drag_validation.py b/tests/test_drag_validation.py
index 56b7f6c..de51818 100644
--- a/tests/test_drag_validation.py
+++ b/tests/test_drag_validation.py
@@ -5 +5,7 @@ import pytest
-from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
+from rocket_sim import (
+    FlightPhase,
+    Simulation,
+    SimulationConfig,
+    ThrustCurve,
+    Vector2,
+)
@@ -13,2 +19 @@ def _run_vertical_fall(dt: float) -> Simulation:
-            thrust_n=0.0,
-            burn_time_s=0.0,
+            thrust_curve=ThrustCurve.zero(),
@@ -83,2 +88 @@ def test_each_zero_aerodynamic_parameter_recovers_prompt_02_motion(
-        "thrust_n": 12.0,
-        "burn_time_s": 2.0,
+        "thrust_curve": ThrustCurve.constant(12.0, 2.0),
diff --git a/tests/test_forces.py b/tests/test_forces.py
index 470ed97..f466dc9 100644
--- a/tests/test_forces.py
+++ b/tests/test_forces.py
@@ -5 +5 @@ import pytest
-from rocket_sim import SimulationConfig, Vector2
+from rocket_sim import SimulationConfig, ThrustCurve, Vector2
@@ -28 +28,3 @@ def test_thrust_components_at_cardinal_angles(
-        thrust_n=10.0, launch_angle_rad=angle, gravity_m_s2=0.0
+        thrust_curve=ThrustCurve.constant(10.0, 1.0),
+        launch_angle_rad=angle,
+        gravity_m_s2=0.0,
@@ -40 +42 @@ def test_net_acceleration_is_force_sum_divided_by_mass() -> None:
-        thrust_n=10.0,
+        thrust_curve=ThrustCurve.constant(10.0, 1.0),
@@ -53 +55,3 @@ def test_thrust_uses_exact_half_open_burn_interval() -> None:
-    config = SimulationConfig(thrust_n=10.0, burn_time_s=burn_time_s)
+    config = SimulationConfig(
+        thrust_curve=ThrustCurve.constant(10.0, burn_time_s)
+    )
diff --git a/tests/test_integrator.py b/tests/test_integrator.py
index 8bfc257..76b89a2 100644
--- a/tests/test_integrator.py
+++ b/tests/test_integrator.py
@@ -5 +5,7 @@ import pytest
-from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
+from rocket_sim import (
+    FlightPhase,
+    Simulation,
+    SimulationConfig,
+    ThrustCurve,
+    Vector2,
+)
@@ -24,2 +30 @@ def test_step_crossing_burnout_is_split_at_exact_boundary() -> None:
-        thrust_n=10.0,
-        burn_time_s=0.75,
+        thrust_curve=ThrustCurve.constant(10.0, 0.75),
@@ -73,2 +78 @@ def test_drag_step_uses_start_velocity_then_updated_velocity_for_position() -> N
-            thrust_n=10.0,
-            burn_time_s=2.0,
+            thrust_curve=ThrustCurve.constant(10.0, 2.0),
@@ -119,2 +123 @@ def test_drag_is_recomputed_for_coast_substep_at_exact_burnout() -> None:
-            thrust_n=4.0,
-            burn_time_s=0.5,
+            thrust_curve=ThrustCurve.constant(4.0, 0.5),
diff --git a/tests/test_propulsion.py b/tests/test_propulsion.py
new file mode 100644
index 0000000..2c9c1fb
--- /dev/null
+++ b/tests/test_propulsion.py
@@ -0,0 +1,199 @@
+from dataclasses import FrozenInstanceError
+import math
+
+import pytest
+
+from rocket_sim import (
+    DEFAULT_EDUCATIONAL_THRUST_CURVE,
+    ThrustCurve,
+    ThrustSample,
+)
+
+
+def _curve(*samples: tuple[float, float]) -> ThrustCurve:
+    return ThrustCurve(ThrustSample(time_s, thrust_n) for time_s, thrust_n in samples)
+
+
+def test_curve_defensively_owns_an_immutable_sample_tuple() -> None:
+    source = [ThrustSample(0.0, 2.0), ThrustSample(1.0, 0.0)]
+    curve = ThrustCurve(source)
+    source.append(ThrustSample(2.0, 0.0))
+
+    assert curve.samples == (ThrustSample(0.0, 2.0), ThrustSample(1.0, 0.0))
+    with pytest.raises(FrozenInstanceError):
+        curve.samples = ()  # type: ignore[misc]
+    with pytest.raises(FrozenInstanceError):
+        curve.samples[0].thrust_n = 3.0  # type: ignore[misc]
+
+
+@pytest.mark.parametrize(
+    "samples",
+    [
+        (),
+        (ThrustSample(0.1, 0.0), ThrustSample(1.0, 0.0)),
+        (ThrustSample(0.0, 1.0),),
+        (ThrustSample(0.0, 1.0), ThrustSample(0.0, 2.0)),
+        (ThrustSample(0.0, 1.0), ThrustSample(0.5, 2.0), ThrustSample(0.4, 0.0)),
+    ],
+)
+def test_invalid_curve_structure_is_rejected(
+    samples: tuple[ThrustSample, ...],
+) -> None:
+    with pytest.raises(ValueError):
+        ThrustCurve(samples)
+
+
+@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
+def test_non_finite_sample_times_are_rejected(value: float) -> None:
+    with pytest.raises(ValueError, match="time_s"):
+        ThrustSample(value, 0.0)
+
+
+@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
+def test_non_finite_sample_thrust_is_rejected(value: float) -> None:
+    with pytest.raises(ValueError, match="thrust_n"):
+        ThrustSample(0.0, value)
+
+
+def test_negative_sample_time_and_thrust_are_rejected() -> None:
+    with pytest.raises(ValueError, match="time_s"):
+        ThrustSample(-0.1, 0.0)
+    with pytest.raises(ValueError, match="thrust_n"):
+        ThrustSample(0.0, -0.1)
+
+
+def test_non_sample_values_are_rejected() -> None:
+    with pytest.raises(TypeError, match="ThrustSample"):
+        ThrustCurve(((0.0, 1.0), (1.0, 0.0)))  # type: ignore[arg-type]
+
+
+def test_zero_curve_is_safe_for_every_metric() -> None:
+    curve = ThrustCurve.zero()
+
+    assert curve.samples == (ThrustSample(0.0, 0.0),)
+    assert curve.burn_duration_s == 0.0
+    assert curve.thrust_at(-1.0) == 0.0
+    assert curve.thrust_at(0.0) == 0.0
+    assert curve.thrust_at(1.0) == 0.0
+    assert curve.delivered_impulse_ns(-1.0) == 0.0
+    assert curve.delivered_impulse_ns(1.0) == 0.0
+    assert curve.total_impulse_ns == 0.0
+    assert curve.average_thrust_n == 0.0
+    assert curve.peak_thrust_n == 0.0
+
+
+def test_constant_curve_preserves_nonzero_burn_end_left_limit_in_impulse() -> None:
+    curve = ThrustCurve.constant(5.0, 2.0)
+
+    assert curve.samples == (ThrustSample(0.0, 5.0), ThrustSample(2.0, 5.0))
+    assert curve.thrust_at(math.nextafter(2.0, 0.0)) == 5.0
+    assert curve.thrust_at(2.0) == 0.0
+    assert curve.total_impulse_ns == 10.0
+    assert curve.delivered_impulse_ns(2.0) == 10.0
+    assert curve.average_thrust_n == 5.0
+    assert curve.peak_thrust_n == 5.0
+
+
+def test_invalid_constant_curve_parameters_are_rejected() -> None:
+    for thrust_n, duration_s in (
+        (-1.0, 1.0),
+        (math.inf, 1.0),
+        (1.0, -1.0),
+        (1.0, math.nan),
+        (1.0, 0.0),
+    ):
+        with pytest.raises(ValueError):
+            ThrustCurve.constant(thrust_n, duration_s)
+
+
+def test_interpolation_and_half_open_boundaries_match_literal_oracle() -> None:
+    curve = _curve((0.0, 2.0), (0.4, 6.0), (1.0, 4.0))
+
+    assert curve.thrust_at(-0.1) == 0.0
+    assert curve.thrust_at(0.0) == 2.0
+    assert curve.thrust_at(0.2) == 4.0
+    assert curve.thrust_at(0.4) == 6.0
+    assert curve.thrust_at(0.7) == pytest.approx(5.0, abs=1e-12)
+    assert curve.thrust_at(math.nextafter(1.0, 0.0)) == pytest.approx(
+        4.0, abs=1e-12
+    )
+    assert curve.thrust_at(1.0) == 0.0
+    assert curve.thrust_at(1.1) == 0.0
+
+
+def test_triangle_rectangle_and_multisegment_impulses_are_exact() -> None:
+    triangle = _curve((0.0, 0.0), (1.0, 6.0), (2.0, 0.0))
+    rectangle = _curve((0.0, 5.0), (2.0, 5.0))
+    multi = _curve((0.0, 2.0), (0.5, 6.0), (1.5, 4.0), (2.0, 8.0))
+
+    assert triangle.total_impulse_ns == 6.0
+    assert rectangle.total_impulse_ns == 10.0
+    assert multi.total_impulse_ns == 10.0
+    assert multi.delivered_impulse_ns(-1.0) == 0.0
+    assert multi.delivered_impulse_ns(0.0) == 0.0
+    assert multi.delivered_impulse_ns(0.25) == pytest.approx(0.75, abs=1e-12)
+    assert multi.delivered_impulse_ns(0.5) == 2.0
+    assert multi.delivered_impulse_ns(1.0) == pytest.approx(4.75, abs=1e-12)
+    assert multi.delivered_impulse_ns(1.5) == 7.0
+    assert multi.delivered_impulse_ns(1.75) == pytest.approx(8.25, abs=1e-12)
+    assert multi.delivered_impulse_ns(2.0) == 10.0
+    assert multi.delivered_impulse_ns(3.0) == 10.0
+    assert multi.average_thrust_n == 5.0
+    assert multi.peak_thrust_n == 8.0
+
+
+def test_delivered_impulse_is_monotonic_and_interval_additive() -> None:
+    curve = _curve((0.0, 0.0), (0.2, 7.0), (0.9, 3.0), (1.1, 0.0))
+    times = (-1.0, 0.0, 0.1, 0.2, 0.6, 0.9, 1.1, 2.0)
+    delivered = [curve.delivered_impulse_ns(time_s) for time_s in times]
+
+    assert delivered == sorted(delivered)
+    assert curve.impulse_between_ns(0.1, 0.9) == pytest.approx(
+        curve.impulse_between_ns(0.1, 0.6)
+        + curve.impulse_between_ns(0.6, 0.9),
+        abs=1e-12,
+    )
+    with pytest.raises(ValueError, match="precede"):
+        curve.impulse_between_ns(0.9, 0.1)
+
+
+@pytest.mark.parametrize("method_name", ["thrust_at", "delivered_impulse_ns"])
+@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
+def test_non_finite_query_times_are_rejected(
+    method_name: str, value: float
+) -> None:
+    curve = ThrustCurve.constant(1.0, 1.0)
+    with pytest.raises(ValueError, match="query time"):
+        getattr(curve, method_name)(value)
+
+
+def test_knot_selection_is_strict_and_ordered() -> None:
+    curve = _curve((0.0, 1.0), (0.1, 2.0), (0.2, 3.0), (0.5, 0.0))
+
+    assert curve.knots_strictly_between(0.0, 0.5) == (0.1, 0.2)
+    assert curve.knots_strictly_between(0.1, 0.5) == (0.2,)
+    assert curve.knots_strictly_between(0.2, 0.2) == ()
+
+
+def test_default_synthetic_curve_metrics_match_independent_trapezoids() -> None:
+    curve = DEFAULT_EDUCATIONAL_THRUST_CURVE
+    expected_samples = (
+        ThrustSample(0.00, 12.0),
+        ThrustSample(0.05, 28.0),
+        ThrustSample(0.12, 24.0),
+        ThrustSample(0.35, 20.0),
+        ThrustSample(0.70, 16.0),
+        ThrustSample(0.95, 8.0),
+        ThrustSample(1.05, 0.0),
+    )
+    independently_summed_areas_ns = 1.00 + 1.82 + 5.06 + 6.30 + 3.00 + 0.40
+
+    assert curve.samples == expected_samples
+    assert curve.burn_duration_s == 1.05
+    assert curve.total_impulse_ns == pytest.approx(
+        independently_summed_areas_ns, abs=1e-12
+    )
+    assert curve.peak_thrust_n == 28.0
+    assert curve.average_thrust_n == pytest.approx(
+        16.74285714285714, abs=1e-12
+    )
diff --git a/tests/test_propulsion_integration.py b/tests/test_propulsion_integration.py
new file mode 100644
index 0000000..0a5b242
--- /dev/null
+++ b/tests/test_propulsion_integration.py
@@ -0,0 +1,302 @@
+import math
+
+import pytest
+
+from rocket_sim import (
+    FlightPhase,
+    Simulation,
+    SimulationConfig,
+    ThrustCurve,
+    ThrustSample,
+    Vector2,
+)
+
+
+def _curve(*samples: tuple[float, float]) -> ThrustCurve:
+    return ThrustCurve(ThrustSample(time_s, thrust_n) for time_s, thrust_n in samples)
+
+
+def test_default_curve_is_launch_admissible_without_ground_support_model() -> None:
+    simulation = Simulation()
+
+    simulation.launch()
+    assert simulation.state.phase is FlightPhase.POWERED
+    assert simulation.state.acceleration_m_s2.y == pytest.approx(2.19, abs=1e-12)
+    assert simulation.step()
+
+    assert simulation.state.time_s == 0.01
+    assert simulation.state.velocity_m_s.y == pytest.approx(0.0379, abs=1e-12)
+    assert simulation.state.position_m.y == pytest.approx(0.000379, abs=1e-12)
+    assert simulation.state.has_lifted_off
+
+
+def test_ground_admission_uses_first_interval_impulse_not_only_ignition_thrust() -> None:
+    curve = _curve((0.0, 0.0), (0.01, 40.0), (0.1, 0.0))
+    simulation = Simulation(
+        SimulationConfig(
+            thrust_curve=curve,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.01,
+        )
+    )
+
+    assert curve.thrust_at(0.0) == 0.0
+    assert curve.impulse_between_ns(0.0, 0.01) == pytest.approx(0.2)
+    simulation.launch()
+
+    assert not simulation.is_finished
+    assert simulation.state.acceleration_m_s2.y == pytest.approx(-9.81)
+    assert simulation.step()
+    assert simulation.state.velocity_m_s.y == pytest.approx(0.1019)
+    assert simulation.state.position_m.y == pytest.approx(0.001019)
+    assert simulation.state.has_lifted_off
+
+
+def test_zero_at_ignition_curve_delivers_positive_finite_interval_impulse_airborne() -> None:
+    curve = _curve(
+        (0.00, 0.0),
+        (0.05, 28.0),
+        (0.12, 24.0),
+        (0.35, 20.0),
+        (0.70, 16.0),
+        (0.95, 8.0),
+        (1.05, 0.0),
+    )
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_curve=curve,
+            launch_angle_rad=math.pi / 2.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.2,
+            initial_position_m=Vector2(0.0, 10.0),
+        )
+    )
+
+    assert curve.thrust_at(0.0) == 0.0
+    assert curve.impulse_between_ns(0.0, 0.01) == pytest.approx(0.028, abs=1e-12)
+    simulation.launch()
+    for _ in range(6):
+        assert simulation.step()
+
+    assert curve.total_impulse_ns == pytest.approx(17.28, abs=1e-12)
+    assert simulation.state.time_s == pytest.approx(1.2, abs=1e-12)
+    assert simulation.state.velocity_m_s.y == pytest.approx(17.28, abs=1e-12)
+
+
+def test_one_outer_step_splits_at_one_knot_and_preserves_outer_step_count() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=2.0,
+            thrust_curve=_curve((0.0, 0.0), (0.2, 4.0), (1.0, 4.0)),
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.5,
+            initial_position_m=Vector2(0.0, 1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    assert simulation.physics_step_count == 1
+    assert simulation.state.velocity_m_s.x == pytest.approx(0.8, abs=1e-12)
+    assert simulation.state.position_m.x == pytest.approx(0.28, abs=1e-12)
+    assert [state.time_s for state in simulation.trajectory].count(0.2) == 1
+
+
+def test_one_outer_step_splits_at_multiple_knots_in_order() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_curve=_curve(
+                (0.0, 0.0),
+                (0.1, 2.0),
+                (0.2, 0.0),
+                (0.3, 4.0),
+                (1.0, 4.0),
+            ),
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.5,
+            initial_position_m=Vector2(0.0, 1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    assert simulation.physics_step_count == 1
+    assert simulation.state.velocity_m_s.x == pytest.approx(1.2, abs=1e-12)
+    assert simulation.state.position_m.x == pytest.approx(0.31, abs=1e-12)
+    assert [state.time_s for state in simulation.trajectory] == [
+        0.0,
+        0.1,
+        0.2,
+        0.3,
+        0.5,
+    ]
+    zero_knot = simulation.trajectory[2]
+    assert zero_knot.phase is FlightPhase.POWERED
+    assert zero_knot.acceleration_m_s2 == Vector2(0.0, 0.0)
+
+
+def test_multiple_knots_recompute_active_drag_from_each_segment_start() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_curve=_curve(
+                (0.0, 0.0), (0.1, 2.0), (0.2, 0.0), (0.4, 0.0)
+            ),
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=2.0,
+            drag_coefficient=1.0,
+            reference_area_m2=0.5,
+            physics_dt_s=0.3,
+            initial_position_m=Vector2(0.0, 1.0),
+            initial_velocity_m_s=Vector2(1.0, 0.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    assert simulation.state.velocity_m_s.x == pytest.approx(
+        1.03493743671875, abs=1e-12
+    )
+    assert simulation.state.position_m.x == pytest.approx(
+        0.317981243671875, abs=1e-12
+    )
+    assert [state.time_s for state in simulation.trajectory] == [
+        0.0,
+        0.1,
+        0.2,
+        0.3,
+    ]
+
+
+def test_non_aligned_burn_end_delivers_exact_impulse_and_transitions_once() -> None:
+    curve = ThrustCurve.constant(4.0, 0.35)
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_curve=curve,
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.2,
+            initial_position_m=Vector2(0.0, 1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+    assert simulation.step()
+
+    assert simulation.state.time_s == 0.4
+    assert simulation.state.velocity_m_s.x == pytest.approx(1.4, abs=1e-12)
+    assert simulation.state.position_m.x == pytest.approx(0.44, abs=1e-12)
+    assert simulation.delivered_impulse_ns == pytest.approx(1.4, abs=1e-12)
+    assert simulation.current_thrust_n == 0.0
+    assert [state.time_s for state in simulation.trajectory].count(0.35) == 1
+    transitions = [
+        (before.phase, after.phase)
+        for before, after in zip(
+            simulation.trajectory, simulation.trajectory[1:], strict=False
+        )
+        if before.phase is not after.phase
+    ]
+    assert transitions == [(FlightPhase.POWERED, FlightPhase.COAST)]
+
+
+def test_impulse_momentum_matches_independent_vector_reference() -> None:
+    curve = _curve((0.0, 2.0), (0.5, 6.0), (1.5, 4.0), (2.0, 8.0))
+    angle = math.radians(30.0)
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=2.0,
+            thrust_curve=curve,
+            launch_angle_rad=angle,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.7,
+            initial_position_m=Vector2(0.0, 10.0),
+            initial_velocity_m_s=Vector2(1.0, -2.0),
+        )
+    )
+    simulation.launch()
+    for _ in range(3):
+        assert simulation.step()
+
+    assert simulation.state.velocity_m_s.x == pytest.approx(
+        1.0 + 5.0 * math.cos(angle), abs=1e-12
+    )
+    assert simulation.state.velocity_m_s.y == pytest.approx(0.5, abs=1e-12)
+
+
+def test_exact_thrust_impulse_and_current_active_drag_telemetry_are_distinct() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=2.0,
+            thrust_curve=_curve((0.0, 2.0), (0.2, 10.0)),
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
+    assert simulation.state.velocity_m_s == Vector2(3.10625, 3.575)
+    assert simulation.state.position_m == Vector2(1.310625, 10.3575)
+    assert simulation.current_thrust_n == pytest.approx(6.0, abs=1e-12)
+    speed = math.hypot(3.10625, 3.575)
+    expected_drag_x = -0.125 * speed * 3.10625
+    expected_drag_y = -0.125 * speed * 3.575
+    assert simulation.current_forces.drag_n.x == pytest.approx(
+        expected_drag_x, abs=1e-12
+    )
+    assert simulation.current_forces.drag_n.y == pytest.approx(
+        expected_drag_y, abs=1e-12
+    )
+    assert simulation.state.acceleration_m_s2.x == pytest.approx(
+        (6.0 + expected_drag_x) / 2.0, abs=1e-12
+    )
+    assert simulation.state.acceleration_m_s2.y == pytest.approx(
+        (-6.0 + expected_drag_y) / 2.0, abs=1e-12
+    )
+
+
+def test_declining_thrust_changes_acceleration_before_burnout() -> None:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_curve=_curve((0.0, 10.0), (0.5, 5.0), (1.0, 0.0)),
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.25,
+            initial_position_m=Vector2(0.0, 1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+    acceleration_at_quarter = simulation.state.acceleration_m_s2.x
+    assert simulation.step()
+    acceleration_at_half = simulation.state.acceleration_m_s2.x
+
+    assert acceleration_at_quarter == pytest.approx(7.5, abs=1e-12)
+    assert acceleration_at_half == pytest.approx(5.0, abs=1e-12)
+    assert simulation.state.phase is FlightPhase.POWERED
+    assert acceleration_at_half < acceleration_at_quarter
diff --git a/tests/test_propulsion_validation.py b/tests/test_propulsion_validation.py
new file mode 100644
index 0000000..470899d
--- /dev/null
+++ b/tests/test_propulsion_validation.py
@@ -0,0 +1,161 @@
+import math
+
+import pytest
+
+from rocket_sim import Simulation, SimulationConfig, ThrustCurve, ThrustSample, Vector2
+
+
+SAMPLES = ((0.0, 4.0), (0.13, 18.0), (0.37, 7.0), (0.73, 0.0))
+
+
+def _production_curve() -> ThrustCurve:
+    return ThrustCurve(ThrustSample(time_s, thrust_n) for time_s, thrust_n in SAMPLES)
+
+
+def _literal_thrust_n(time_s: float) -> float:
+    if time_s < 0.0 or time_s >= 0.73:
+        return 0.0
+    for (left_t, left_n), (right_t, right_n) in zip(
+        SAMPLES, SAMPLES[1:], strict=False
+    ):
+        if left_t <= time_s < right_t:
+            fraction = (time_s - left_t) / (right_t - left_t)
+            return left_n + fraction * (right_n - left_n)
+    raise AssertionError("literal curve interval not found")
+
+
+def _independent_rk4_reference(duration_s: float) -> tuple[float, float, float, float]:
+    mass_kg = 2.0
+    angle_rad = 0.3
+    gravity_m_s2 = 3.0
+    drag_k = 0.5 * 1.2 * 0.8 * 0.15
+    state = (0.0, 100.0, 2.0, 1.0)
+    time_s = 0.0
+    dt_s = 1.0e-5
+
+    def derivative(
+        derivative_time_s: float,
+        derivative_state: tuple[float, float, float, float],
+    ) -> tuple[float, float, float, float]:
+        _, _, vx_m_s, vy_m_s = derivative_state
+        speed_m_s = math.hypot(vx_m_s, vy_m_s)
+        thrust_n = _literal_thrust_n(derivative_time_s)
+        drag_x_n = -drag_k * speed_m_s * vx_m_s
+        drag_y_n = -drag_k * speed_m_s * vy_m_s
+        return (
+            vx_m_s,
+            vy_m_s,
+            (thrust_n * math.cos(angle_rad) + drag_x_n) / mass_kg,
+            (
+                thrust_n * math.sin(angle_rad)
+                - mass_kg * gravity_m_s2
+                + drag_y_n
+            )
+            / mass_kg,
+        )
+
+    while time_s < duration_s:
+        step_s = min(dt_s, duration_s - time_s)
+        k1 = derivative(time_s, state)
+        k2_state = tuple(
+            value + 0.5 * step_s * slope
+            for value, slope in zip(state, k1, strict=True)
+        )
+        k2 = derivative(time_s + 0.5 * step_s, k2_state)
+        k3_state = tuple(
+            value + 0.5 * step_s * slope
+            for value, slope in zip(state, k2, strict=True)
+        )
+        k3 = derivative(time_s + 0.5 * step_s, k3_state)
+        k4_state = tuple(
+            value + step_s * slope
+            for value, slope in zip(state, k3, strict=True)
+        )
+        k4 = derivative(time_s + step_s, k4_state)
+        state = tuple(
+            value
+            + (step_s / 6.0)
+            * (slope1 + 2.0 * slope2 + 2.0 * slope3 + slope4)
+            for value, slope1, slope2, slope3, slope4 in zip(
+                state, k1, k2, k3, k4, strict=True
+            )
+        )
+        time_s += step_s
+    return state
+
+
+def _run_active_drag(dt_s: float, duration_s: float = 0.6) -> Simulation:
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=2.0,
+            thrust_curve=_production_curve(),
+            launch_angle_rad=0.3,
+            gravity_m_s2=3.0,
+            air_density_kg_m3=1.2,
+            drag_coefficient=0.8,
+            reference_area_m2=0.15,
+            physics_dt_s=dt_s,
+            initial_position_m=Vector2(0.0, 100.0),
+            initial_velocity_m_s=Vector2(2.0, 1.0),
+        )
+    )
+    simulation.launch()
+    for _ in range(round(duration_s / dt_s)):
+        assert simulation.step()
+    return simulation
+
+
+def test_sampled_thrust_with_active_drag_converges_against_independent_rk4() -> None:
+    reference_x, reference_y, reference_vx, reference_vy = (
+        _independent_rk4_reference(0.6)
+    )
+    simulations = [_run_active_drag(dt_s) for dt_s in (0.02, 0.01, 0.005)]
+    position_errors = [
+        math.hypot(
+            simulation.state.position_m.x - reference_x,
+            simulation.state.position_m.y - reference_y,
+        )
+        for simulation in simulations
+    ]
+    velocity_errors = [
+        math.hypot(
+            simulation.state.velocity_m_s.x - reference_vx,
+            simulation.state.velocity_m_s.y - reference_vy,
+        )
+        for simulation in simulations
+    ]
+
+    assert position_errors[0] > position_errors[1] > position_errors[2]
+    assert velocity_errors[0] > velocity_errors[1] > velocity_errors[2]
+    for errors in (position_errors, velocity_errors):
+        assert 1.7 < errors[0] / errors[1] < 2.3
+        assert 1.7 < errors[1] / errors[2] < 2.3
+
+
+@pytest.mark.parametrize("dt_s", [0.02, 0.01, 0.005])
+def test_propulsion_only_final_velocity_is_timestep_independent(dt_s: float) -> None:
+    angle_rad = 0.3
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=2.0,
+            thrust_curve=_production_curve(),
+            launch_angle_rad=angle_rad,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=dt_s,
+            initial_position_m=Vector2(0.0, 100.0),
+            initial_velocity_m_s=Vector2(2.0, 1.0),
+        )
+    )
+    simulation.launch()
+    for _ in range(round(0.8 / dt_s)):
+        assert simulation.step()
+
+    independently_summed_impulse_ns = 1.43 + 3.00 + 1.26
+    delta_speed_m_s = independently_summed_impulse_ns / 2.0
+    assert simulation.state.velocity_m_s.x == pytest.approx(
+        2.0 + delta_speed_m_s * math.cos(angle_rad), abs=1e-11
+    )
+    assert simulation.state.velocity_m_s.y == pytest.approx(
+        1.0 + delta_speed_m_s * math.sin(angle_rad), abs=1e-11
+    )
diff --git a/tests/test_rendering.py b/tests/test_rendering.py
index 23e807f..a3add4e 100644
--- a/tests/test_rendering.py
+++ b/tests/test_rendering.py
@@ -11 +11,8 @@ import pygame
-from rocket_sim import ForceBreakdown, Simulation, SimulationConfig, Vector2
+from rocket_sim import (
+    ForceBreakdown,
+    Simulation,
+    SimulationConfig,
+    ThrustCurve,
+    ThrustSample,
+    Vector2,
+)
@@ -17,0 +25 @@ from rocket_sim.rendering import (
+    thrust_timeline_geometry,
@@ -69 +77 @@ def test_core_modules_do_not_depend_on_pygame() -> None:
-    for module_name in ("config.py", "physics.py", "simulation.py"):
+    for module_name in ("config.py", "physics.py", "propulsion.py", "simulation.py"):
@@ -157 +165 @@ def test_inspector_contains_required_state_parameters_forces_and_equations() ->
-        "Ft = T(cos(theta), sin(theta))",
+        "Ft(t) = T(t) (cos(theta), sin(theta))",
@@ -160,0 +169 @@ def test_inspector_contains_required_state_parameters_forces_and_equations() ->
+        "I = integral T(t) dt",
@@ -164,0 +174,8 @@ def test_inspector_contains_required_state_parameters_forces_and_equations() ->
+        "Motor phase: READY",
+        "Current thrust:",
+        "Burn-time progress:",
+        "Burn duration:   1.050 s",
+        "Peak stored thrust:  28.000 N",
+        "Average thrust:  16.743 N",
+        "Delivered impulse:   0.000 N*s",
+        "Total impulse:  17.580 N*s",
@@ -172,0 +190,112 @@ def test_inspector_contains_required_state_parameters_forces_and_equations() ->
+def test_inspector_motor_values_use_production_curve_and_simulation_time() -> None:
+    curve = ThrustCurve(
+        (
+            ThrustSample(0.0, 2.0),
+            ThrustSample(1.0, 6.0),
+            ThrustSample(2.0, 4.0),
+        )
+    )
+    simulation = Simulation(
+        SimulationConfig(
+            thrust_curve=curve,
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.5,
+            initial_position_m=Vector2(0.0, 1.0),
+        )
+    )
+    simulation.launch()
+    assert simulation.step()
+
+    text = "\n".join(
+        physics_inspector_rows(simulation, simulation.current_forces)
+    )
+
+    for expected in (
+        "Motor phase: ACTIVE",
+        "Current thrust:   4.000 N",
+        "Burn-time progress:  25.00%",
+        "Burn duration:   2.000 s",
+        "Peak stored thrust:   6.000 N",
+        "Average thrust:   4.500 N",
+        "Delivered impulse:   1.500 N*s",
+        "Total impulse:   9.000 N*s",
+    ):
+        assert expected in text
+
+
+def test_timeline_geometry_maps_exact_production_samples_and_clamped_cursor() -> None:
+    curve = ThrustCurve(
+        (
+            ThrustSample(0.0, 2.0),
+            ThrustSample(1.0, 6.0),
+            ThrustSample(2.0, 4.0),
+        )
+    )
+    graph = pygame.Rect(10, 20, 200, 100)
+
+    active = thrust_timeline_geometry(curve, 0.5, 4.0, graph)
+    coast = thrust_timeline_geometry(curve, 3.0, 0.0, graph)
+
+    assert active.sample_points_px == ((10, 87), (110, 20), (210, 53))
+    assert active.cursor_x_px == 60
+    assert active.burnout_x_px == 210
+    assert active.current_thrust_n == 4.0
+    assert active.cursor_time_s == 0.5
+    assert active.burnout_zero_point_px == (210, 120)
+    assert active.terminal_sample_is_left_limit
+    assert coast.cursor_x_px == 210
+    assert coast.current_thrust_n == 0.0
+    assert coast.cursor_time_s == 2.0
+
+
+def test_timeline_distinguishes_nonzero_terminal_left_limit_from_burnout_zero() -> None:
+    curve = ThrustCurve.constant(10.0, 1.0)
+    geometry = thrust_timeline_geometry(
+        curve, 1.0, curve.thrust_at(1.0), pygame.Rect(10, 20, 200, 100)
+    )
+
+    assert geometry.sample_points_px[-1] == (210, 20)
+    assert geometry.burnout_zero_point_px == (210, 120)
+    assert geometry.terminal_sample_is_left_limit
+    assert geometry.current_thrust_n == 0.0
+
+
+def test_renderer_timeline_receives_configured_curve_and_current_time() -> None:
+    pygame.init()
+    try:
+        curve = ThrustCurve(
+            (ThrustSample(0.0, 3.0), ThrustSample(0.3, 0.0))
+        )
+        simulation = Simulation(
+            SimulationConfig(
+                thrust_curve=curve,
+                gravity_m_s2=0.0,
+                initial_position_m=Vector2(0.0, 1.0),
+            )
+        )
+        simulation.launch()
+        assert simulation.step()
+        surface = pygame.Surface((1200, 720))
+        renderer = Renderer()
+
+        with patch(
+            "rocket_sim.rendering.thrust_timeline_geometry",
+            wraps=thrust_timeline_geometry,
+        ) as geometry_spy:
+            renderer.draw(surface, simulation)
+
+        geometry_spy.assert_called_once()
+        assert geometry_spy.call_args.args[0] is curve
+        assert geometry_spy.call_args.args[1] == simulation.state.time_s
+        assert geometry_spy.call_args.args[2] == simulation.current_thrust_n
+        rendering_source = (
+            Path(__file__).parents[1] / "src" / "rocket_sim" / "rendering.py"
+        ).read_text()
+        assert "ThrustSample(" not in rendering_source
+        assert "impulse_between_ns" not in rendering_source
+    finally:
+        pygame.quit()
+
+
@@ -175 +304 @@ def test_inspector_distinguishes_no_liftoff_from_impact() -> None:
-        SimulationConfig(thrust_n=0.0, burn_time_s=0.0)
+        SimulationConfig(thrust_curve=ThrustCurve.zero())
@@ -186,0 +316,10 @@ def test_inspector_distinguishes_no_liftoff_from_impact() -> None:
+def test_zero_duration_curve_has_explicit_no_burn_inspector_status() -> None:
+    simulation = Simulation(SimulationConfig(thrust_curve=ThrustCurve.zero()))
+    rows = physics_inspector_rows(simulation, simulation.current_forces)
+    text = "\n".join(rows)
+
+    assert "Burnout: zero-duration curve (no burn)" in text
+    assert "Motor phase: READY / NO BURN" in text
+    assert "Burn-time progress: N/A (zero-duration)" in text
+
+
diff --git a/tests/test_simulation.py b/tests/test_simulation.py
index 7e0050b..c8041b4 100644
--- a/tests/test_simulation.py
+++ b/tests/test_simulation.py
@@ -5 +5,8 @@ import pytest
-from rocket_sim import FlightPhase, Simulation, SimulationConfig, Vector2
+from rocket_sim import (
+    FlightPhase,
+    Simulation,
+    SimulationConfig,
+    ThrustCurve,
+    ThrustSample,
+    Vector2,
+)
@@ -34,2 +41 @@ def test_ground_crossing_is_linearly_interpolated_on_discrete_segment() -> None:
-            thrust_n=0.0,
-            burn_time_s=0.0,
+            thrust_curve=ThrustCurve.zero(),
@@ -56,2 +62 @@ def test_accelerated_ground_crossing_interpolates_impact_velocity() -> None:
-            thrust_n=0.0,
-            burn_time_s=0.0,
+            thrust_curve=ThrustCurve.zero(),
@@ -78 +83 @@ def test_ground_configuration_that_cannot_lift_off_terminates_without_motion() -
-        SimulationConfig(thrust_n=0.0, burn_time_s=0.0, gravity_m_s2=9.81)
+        SimulationConfig(thrust_curve=ThrustCurve.zero(), gravity_m_s2=9.81)
@@ -92,2 +97 @@ def test_under_resolved_ground_launch_never_records_negative_altitude() -> None:
-            thrust_n=0.0,
-            burn_time_s=0.0,
+            thrust_curve=ThrustCurve.zero(),
@@ -123,2 +127 @@ def test_pre_burn_impact_telemetry_keeps_thrust_and_acceleration_consistent() ->
-            thrust_n=1.0,
-            burn_time_s=1.0,
+            thrust_curve=ThrustCurve.constant(1.0, 1.0),
@@ -142,0 +146,35 @@ def test_pre_burn_impact_telemetry_keeps_thrust_and_acceleration_consistent() ->
+def test_time_varying_thrust_impact_preserves_interpolated_event_contract() -> None:
+    curve = ThrustCurve(
+        (ThrustSample(0.0, 2.0), ThrustSample(1.0, 10.0))
+    )
+    simulation = Simulation(
+        SimulationConfig(
+            mass_kg=1.0,
+            thrust_curve=curve,
+            launch_angle_rad=0.0,
+            gravity_m_s2=0.0,
+            air_density_kg_m3=0.0,
+            physics_dt_s=0.2,
+            initial_position_m=Vector2(0.0, 0.1),
+            initial_velocity_m_s=Vector2(0.0, -1.0),
+        )
+    )
+    simulation.launch()
+
+    assert simulation.step()
+
+    assert simulation.is_finished
+    assert simulation.state.time_s == pytest.approx(0.1)
+    assert simulation.state.position_m.x == pytest.approx(0.056)
+    assert simulation.state.position_m.y == 0.0
+    assert simulation.state.velocity_m_s.x == pytest.approx(0.28)
+    assert simulation.state.velocity_m_s.y == -1.0
+    assert simulation.current_thrust_n == pytest.approx(2.8)
+    assert simulation.delivered_impulse_ns == pytest.approx(0.24)
+    assert simulation.state.acceleration_m_s2.x == pytest.approx(2.8)
+    assert simulation.state.acceleration_m_s2.y == 0.0
+    assert simulation.state.velocity_m_s.x != pytest.approx(
+        simulation.delivered_impulse_ns
+    )
+
+
@@ -147,2 +185 @@ def test_drag_telemetry_uses_interpolated_impact_velocity() -> None:
-            thrust_n=1.0,
-            burn_time_s=1.0,
+            thrust_curve=ThrustCurve.constant(1.0, 1.0),
@@ -197,0 +235,3 @@ def test_reset_reproduces_state_history_and_clears_fractional_accumulator() -> N
+    first_forces = simulation.current_forces
+    first_delivered_impulse = simulation.delivered_impulse_ns
+    first_config = simulation.config
@@ -210,0 +251,3 @@ def test_reset_reproduces_state_history_and_clears_fractional_accumulator() -> N
+    assert simulation.current_forces == first_forces
+    assert simulation.delivered_impulse_ns == first_delivered_impulse
+    assert simulation.config == first_config
@@ -287 +330 @@ def test_paused_single_step_preserves_burnout_split() -> None:
-            burn_time_s=0.015,
+            thrust_curve=ThrustCurve.constant(20.0, 0.015),
@@ -304,0 +348,26 @@ def test_paused_single_step_preserves_burnout_split() -> None:
+def test_paused_single_step_crosses_sample_knot_and_updates_motor_observables() -> None:
+    paused = Simulation(SimulationConfig(physics_dt_s=0.04))
+    running = Simulation(SimulationConfig(physics_dt_s=0.04))
+    for simulation in (paused, running):
+        simulation.launch()
+        assert simulation.step()
+
+    paused.advance_elapsed(0.005)
+    paused.toggle_pause()
+    before_impulse = paused.delivered_impulse_ns
+    before_thrust = paused.current_thrust_n
+    before_accumulator = paused.accumulator_s
+
+    assert paused.single_step_paused()
+    assert running.step()
+
+    assert paused.is_paused
+    assert paused.state == running.state
+    assert paused.trajectory == running.trajectory
+    assert paused.accumulator_s == before_accumulator
+    assert [state.time_s for state in paused.trajectory].count(0.05) == 1
+    assert paused.delivered_impulse_ns > before_impulse
+    assert paused.current_thrust_n != before_thrust
+    assert paused.current_forces == running.current_forces
+
+
@@ -313 +382 @@ def test_paused_single_step_is_inactive_when_not_paused_live_flight() -> None:
-        SimulationConfig(thrust_n=0.0, burn_time_s=0.0)
+        SimulationConfig(thrust_curve=ThrustCurve.zero())
diff --git a/tests/test_time_accumulator.py b/tests/test_time_accumulator.py
index 5b60517..3740489 100644
--- a/tests/test_time_accumulator.py
+++ b/tests/test_time_accumulator.py
@@ -5 +5 @@ import pytest
-from rocket_sim import Simulation, SimulationConfig
+from rocket_sim import Simulation, SimulationConfig, ThrustCurve
@@ -19 +19 @@ def _run_partitioned(
-            burn_time_s=burn_time_s,
+            thrust_curve=ThrustCurve.constant(20.0, burn_time_s),
@@ -68,0 +69,38 @@ def test_active_drag_results_are_independent_of_30_60_144_fps_partitions() -> No
+def test_sampled_thrust_and_drag_are_independent_of_30_60_144_fps_partitions() -> None:
+    def run(fps: int) -> Simulation:
+        simulation = Simulation()
+        simulation.launch()
+        total_s = 0.5
+        frame_s = 1.0 / fps
+        elapsed_s = 0.0
+        while elapsed_s + frame_s < total_s:
+            simulation.advance_elapsed(frame_s)
+            elapsed_s += frame_s
+        simulation.advance_elapsed(total_s - elapsed_s)
+        return simulation
+
+    simulations = [run(fps) for fps in (30, 60, 144)]
+
+    for simulation in simulations:
+        assert simulation.physics_step_count == 50
+        assert simulation.state.time_s == pytest.approx(0.5, abs=1e-12)
+    assert simulations[0].state == simulations[1].state == simulations[2].state
+    assert (
+        simulations[0].trajectory
+        == simulations[1].trajectory
+        == simulations[2].trajectory
+    )
+    assert (
+        simulations[0].current_forces
+        == simulations[1].current_forces
+        == simulations[2].current_forces
+    )
+    assert (
+        simulations[0].delivered_impulse_ns
+        == simulations[1].delivered_impulse_ns
+        == simulations[2].delivered_impulse_ns
+    )
+    for simulation in simulations:
+        assert simulation.accumulator_s == pytest.approx(0.0, abs=1e-12)
+
+
~~~~~~~
